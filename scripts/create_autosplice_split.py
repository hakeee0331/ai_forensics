import argparse
import csv
import random
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def create_split(archive, output, seed=42):
    with ZipFile(archive) as dataset:
        names = [name for name in dataset.namelist() if name.startswith("AutoSplice/Authentic/") and name.endswith(".jpg")]
        ids = sorted({PurePosixPath(name).stem for name in names}, key=int)
    if not ids:
        raise ValueError("AutoSplice 원본 ID가 있어야 함.")

    random.Random(seed).shuffle(ids)
    train_end = len(ids) * 80 // 100
    val_end = train_end + len(ids) * 10 // 100
    assignments = {}
    for index, original_id in enumerate(ids):
        assignments[original_id] = "train" if index < train_end else "val" if index < val_end else "test"

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["original_id", "split"])
        for original_id in sorted(assignments, key=int):
            writer.writerow([original_id, assignments[original_id]])
    return assignments


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = create_split(args.archive, args.output, args.seed)
    print({split: list(result.values()).count(split) for split in ("train", "val", "test")})
