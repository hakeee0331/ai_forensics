"""003에서 확인한 CAT-Net v2 준비·로드·JPEG 추론을 제공함."""

import importlib
import shutil
import subprocess
import sys
import tempfile
from glob import escape
from functools import lru_cache
from pathlib import Path

from .datasets import sha256

CODE_URL = "https://github.com/mjkwon2021/CAT-Net.git"
CODE_COMMIT = "5eb85900b0e72423c95a8d41bc835b86c8671f8a"
WEIGHT_SHA256 = "f82aaafdd1142775231feedcea0bb7027f7370561d9e8d107465454001865989"


def _git(code_dir, *args):
    result = subprocess.run(["git", "-C", str(code_dir), *args], check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _check_code(code_dir):
    code_dir = Path(code_dir).resolve()
    if not (code_dir / ".git").exists():
        raise FileNotFoundError("공식 저장소 복제본을 준비해야 함.")
    if _git(code_dir, "rev-parse", "HEAD") != CODE_COMMIT:
        raise ValueError(f"003의 공식 코드 커밋을 사용해야 함: {CODE_COMMIT}")
    if _git(code_dir, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("공식 코드 폴더의 변경·추가 파일을 확인해야 함. 새 경로에 준비하는 것을 권장함.")
    for relative in ("lib/models/network_CAT.py", "experiments/CAT_full.yaml", "Splicing/data/dataset_arbitrary.py"):
        if not (code_dir / relative).is_file():
            raise FileNotFoundError(f"공식 코드 파일이 필요함: {relative}")
    return code_dir


def prepare_code(code_dir):
    """새 경로에 공식 코드를 복제하고 003의 커밋으로 고정함. 기존 경로는 검사만 함."""
    code_dir = Path(code_dir).resolve()
    if not code_dir.exists():
        code_dir.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=code_dir.parent) as temporary:
            checkout = Path(temporary) / "CAT-Net"
            subprocess.run(["git", "clone", CODE_URL, str(checkout)], check=True)
            _git(checkout, "checkout", "--detach", CODE_COMMIT)
            _check_code(checkout)
            checkout.rename(code_dir)
    _check_code(code_dir)
    print("공식 코드:", code_dir)
    print("코드 커밋:", CODE_COMMIT)
    return code_dir


def prepare_weights(source, destination):
    """003 가중치를 해시로 확인하고 복사함. 같은 복사본은 재사용함."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if sha256(source) != WEIGHT_SHA256:
        raise ValueError("003에서 확인한 CAT_full_v2 가중치와 일치해야 함.")
    if destination.is_file() and sha256(destination) == WEIGHT_SHA256:
        print("기존 가중치 복사본을 사용함.")
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as file:
        temporary = Path(file.name)
    try:
        shutil.copyfile(source, temporary)
        if sha256(temporary) != WEIGHT_SHA256:
            raise ValueError("가중치 복사본의 SHA-256이 일치해야 함.")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print("가중치 복사·해시 확인 완료:", destination)
    return destination


def _official_modules(code_dir):
    # lib 등 이름이 같은 다른 모듈을 조용히 재사용하지 않도록 확인함.
    for name, module in list(sys.modules.items()):
        if name.split(".")[0] not in ("lib", "Splicing", "project_config"):
            continue
        locations = list(getattr(module, "__path__", []))
        if getattr(module, "__file__", None):
            locations.append(module.__file__)
        if not locations or any(not Path(path).resolve().is_relative_to(code_dir) for path in locations):
            raise RuntimeError(f"다른 경로의 {name} 모듈이 로드돼 있음. 커널을 재시작해야 함.")
    if str(code_dir) in sys.path:
        sys.path.remove(str(code_dir))
    sys.path.insert(0, str(code_dir))
    importlib.invalidate_caches()
    config = importlib.import_module("lib.config").config
    network = importlib.import_module("lib.models.network_CAT")
    dataset = importlib.import_module("Splicing.data.dataset_arbitrary")
    for module in (network, dataset):
        if not Path(module.__file__).resolve().is_relative_to(code_dir):
            raise RuntimeError("공식 모듈의 import 경로를 확인하고 커널을 재시작해야 함.")
    return config, network.CAT_Net, dataset.arbitrary


@lru_cache(maxsize=1)
def _input_dataset(code_dir):
    # 이미지마다 Git 검사와 공식 모듈 경로 검사를 반복하지 않도록 함.
    code_dir = _check_code(code_dir)
    _, _, dataset_class = _official_modules(code_dir)
    return dataset_class


def prepare_input(image_path, code_dir):
    """JPEG의 CPU 입력 텐서·양자화 테이블·원본 (H, W)를 반환함. 배치 축은 붙이지 않음."""
    from PIL import Image

    image_path = Path(image_path).resolve()
    with Image.open(image_path) as image:
        if image.format != "JPEG":
            raise ValueError("현재는 JPEG 입력만 지원함. 비 JPEG 변환 조건은 별도로 정해야 함.")
        width, height = image.size
    dataset_class = _input_dataset(Path(code_dir).resolve())
    dataset = dataset_class(crop_size=None, grid_crop=True, blocks=("RGB", "DCTvol", "qtable"),
                            DCT_channels=1, tamp_list=escape(str(image_path)), read_from_jpeg=True)
    tensor, _, qtable = dataset.get_tamp(0)
    return tensor, qtable, (height, width)


class CatNetDetector:
    """CAT_full_v2의 단일 JPEG 추론을 제공함. 임계값·평가·시각화는 호출부에서 처리함."""

    def __init__(self, model, code_dir, device, info):
        self.model = model
        self.code_dir = Path(code_dir).resolve()
        self.device = device
        self.info = info

    @classmethod
    def from_pretrained(cls, code_dir, weight_path, device="cuda"):
        """준비된 공식 코드와 003의 전체 가중치를 검사하고 모델을 로드함."""
        import torch

        code_dir = _check_code(code_dir)
        weight_path = Path(weight_path).resolve()
        if sha256(weight_path) != WEIGHT_SHA256:
            raise ValueError("003에서 확인한 CAT_full_v2 가중치와 일치해야 함.")
        device = torch.device(device)
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA 장치를 사용할 수 있어야 함.")
        config, model_class, _ = _official_modules(code_dir)
        cfg = config.clone()
        cfg.defrost()
        cfg.merge_from_file(str(code_dir / "experiments/CAT_full.yaml"))
        cfg.freeze()
        model = model_class(cfg)
        # 003과 같은 전체 체크포인트 형식임. 위에서 확인한 해시에 한해서 읽음.
        checkpoint = torch.load(weight_path, map_location="cpu", weights_only=False)
        model.load_state_dict(checkpoint["state_dict"], strict=True)
        info = dict(code_commit=CODE_COMMIT, code_dir=str(code_dir), weight_path=str(weight_path),
                    weight_sha256=WEIGHT_SHA256, weight_bytes=weight_path.stat().st_size,
                    epoch=checkpoint.get("epoch"), parameters=sum(p.numel() for p in model.parameters()),
                    device=str(device), wrapper_sha256=sha256(__file__),
                    resize="bilinear", align_corners=False)
        del checkpoint
        model.to(device).eval()
        return cls(model, code_dir, device, info)

    def predict_proba(self, image_path):
        """JPEG 한 장의 조작 확률을 원본 크기 (H, W)의 float32 NumPy 배열로 반환함."""
        import numpy as np
        import torch
        from torch.nn import functional as F

        tensor, qtable, (height, width) = prepare_input(image_path, self.code_dir)
        x = tensor.unsqueeze(0).to(self.device)
        q = qtable.unsqueeze(0).to(self.device)
        self.model.eval()
        with torch.inference_mode():
            logits = self.model(x, q)
            logits = F.interpolate(logits, size=x.shape[-2:], mode="bilinear", align_corners=False)
            probability = torch.softmax(logits, dim=1)[0, 1, :height, :width].cpu().numpy().copy()
        if probability.shape != (height, width) or not np.isfinite(probability).all():
            raise ValueError("예측 크기가 원본과 같고 확률이 유한해야 함.")
        return probability
