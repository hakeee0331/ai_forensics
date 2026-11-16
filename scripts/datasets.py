import csv
import hashlib
import shutil
from pathlib import Path
from zipfile import ZipFile


def sha256(path):
    """파일을 나누어 읽고 SHA-256을 반환함."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare_dataset_zip(source, runtime_zip, destination, expected_hash):
    """ZIP을 복사·검증·해제하고 해제 경로를 반환함. 완료된 해제는 재사용함."""
    source, runtime_zip, destination = Path(source), Path(runtime_zip), Path(destination)
    if not source.is_file():
        raise FileNotFoundError(f"데이터 ZIP 경로를 확인해야 함: {source}")
    runtime_zip.parent.mkdir(parents=True, exist_ok=True)
    if not runtime_zip.is_file() or sha256(runtime_zip) != expected_hash:
        shutil.copyfile(source, runtime_zip)
    if sha256(runtime_zip) != expected_hash:
        raise ValueError(f"확인한 데이터 ZIP과 일치해야 함: {source.name}")

    marker = destination / f".{source.stem}.complete"
    if marker.is_file() and marker.read_text() == expected_hash:
        print(source.stem, "기존 해제 파일 사용")
        return destination

    destination.mkdir(parents=True, exist_ok=True)
    marker.unlink(missing_ok=True)
    with ZipFile(runtime_zip) as archive:
        archive.extractall(destination)
    marker.write_text(expected_hash)
    print(source.stem, "ZIP SHA-256 확인 및 압축 해제 완료")
    return destination


def autosplice_records(root, split_path, quality=100):
    """원본 ID 분할을 정상 이미지와 조작본에 적용함."""
    root = Path(root)
    if quality not in (100, 90, 75):
        raise ValueError("JPEG 품질은 100, 90, 75 중 하나여야 함.")
    with Path(split_path).open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    assignments = {row["original_id"]: row["split"] for row in rows}
    authentic = sorted((root / "Authentic").glob("*.jpg"))
    if len(assignments) != len(rows) or set(assignments.values()) != {"train", "val", "test"}:
        raise ValueError("분할 목록의 ID는 중복 없이 train, val, test에 배정되어야 함.")
    if not authentic or set(assignments) != {path.stem for path in authentic}:
        raise ValueError("분할 목록과 정상 이미지의 원본 ID가 일치해야 함.")

    records = []
    for path in authentic:
        records.append(dict(dataset="AutoSplice", original_id=path.stem, split=assignments[path.stem],
                            kind="normal", image_path=path, mask_path=None, real_path=path))
    forged = sorted((root / f"Forged_JPEG{quality}").glob("*.jpg"))
    if not forged:
        raise ValueError("선택한 품질의 조작 이미지가 있어야 함.")
    for path in forged:
        original_id = path.stem.rsplit("_", 1)[0]
        mask = root / "Mask" / f"{original_id}_mask.png"
        real = root / "Authentic" / f"{original_id}.jpg"
        if original_id not in assignments or not mask.is_file() or not real.is_file():
            raise ValueError(f"조작본의 원본과 마스크를 확인해야 함: {path.name}")
        records.append(dict(dataset="AutoSplice", original_id=original_id, split=assignments[original_id],
                            kind="manipulated", image_path=path, mask_path=mask, real_path=real))
    return records


def cocoglide_records(root):
    """table.csv의 대응 경로를 읽고 외부 테스트용으로 표시함."""
    root = Path(root)
    with (root / "table.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows or len({row["real"] for row in rows}) != len(rows):
        raise ValueError("table.csv에 중복 없는 원본 경로가 있어야 함.")

    records = []
    for row in rows:
        real, fake, mask = (root / row[key] for key in ("real", "fake", "mask"))
        if not all(path.is_file() for path in (real, fake, mask)):
            raise ValueError(f"table.csv의 이미지와 마스크 경로를 확인해야 함: {row['fake']}")
        original_id = real.stem.rsplit("_", 1)[-1]
        records.append(dict(dataset="CocoGlide", original_id=original_id, split="external_test",
                            kind="normal", image_path=real, mask_path=None, real_path=real))
        records.append(dict(dataset="CocoGlide", original_id=original_id, split="external_test",
                            kind="manipulated", image_path=fake, mask_path=mask, real_path=real))
    return records
