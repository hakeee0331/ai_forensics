"""RGB·마스크 읽기, 같은 위치 크롭, ELA 생성을 처리함."""

from io import BytesIO
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from PIL import Image

PathLike = Union[str, Path]


def _validate_rgb(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb)
    if rgb.ndim != 3 or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 1:
        raise ValueError("RGB는 비어 있지 않은 (H, W, 3) 배열이어야 함.")
    if rgb.dtype != np.uint8:
        raise ValueError("RGB는 0~255 범위의 uint8 배열이어야 함.")
    return rgb


def _validate_mask(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask)
    if mask.ndim != 2 or mask.size == 0:
        raise ValueError("마스크는 비어 있지 않은 (H, W) 배열이어야 함.")
    if not np.isin(mask, (0, 1)).all():
        raise ValueError("마스크는 0(정상), 1(조작)만 포함해야 함.")
    return mask.astype(np.uint8, copy=False)


def load_rgb(path: PathLike) -> np.ndarray:
    """RGB uint8 배열을 반환함. 크기와 EXIF 방향은 변경하지 않음."""
    with Image.open(path) as image:
        return np.array(image.convert("RGB"), dtype=np.uint8)


def load_binary_mask(path: PathLike, *, foreground_value: int) -> np.ndarray:
    """배경 0은 0, 지정한 전경값은 1로 변환함. EXIF 방향은 변경하지 않음."""
    if not isinstance(foreground_value, int) or isinstance(foreground_value, bool):
        raise ValueError("foreground_value는 양의 정수여야 함.")
    if foreground_value <= 0:
        raise ValueError("배경값은 0이며 foreground_value는 양수여야 함.")
    with Image.open(path) as image:
        mask = np.array(image)
    if mask.ndim != 2 or mask.size == 0:
        raise ValueError("마스크는 비어 있지 않은 단일 채널 배열이어야 함.")
    if not np.isin(mask, (0, foreground_value)).all():
        raise ValueError("마스크에는 배경 0과 지정한 전경값만 있어야 함.")
    return (mask == foreground_value).astype(np.uint8)


def crop_pair(rgb: np.ndarray, mask: np.ndarray, *, top: int, left: int,
              height: int, width: int) -> Tuple[np.ndarray, np.ndarray]:
    """이미지와 마스크를 지정한 위치·크기로 자름. 좌표 선택과 보간은 하지 않음."""
    rgb = _validate_rgb(rgb)
    mask = _validate_mask(mask)
    if rgb.shape[:2] != mask.shape:
        raise ValueError("이미지와 마스크의 높이·너비가 일치해야 함.")
    for value in (top, left, height, width):
        if not isinstance(value, (int, np.integer)) or isinstance(value, (bool, np.bool_)):
            raise ValueError("크롭 좌표·크기는 정수여야 함.")
    if top < 0 or left < 0 or height <= 0 or width <= 0:
        raise ValueError("좌표는 0 이상, 크기는 양수여야 함.")
    if top + height > mask.shape[0] or left + width > mask.shape[1]:
        raise ValueError("크롭 영역은 이미지 경계 안에 있어야 함.")
    region = (slice(top, top + height), slice(left, left + width))
    return rgb[region].copy(), mask[region].copy()


def make_ela(rgb: np.ndarray, *, quality: int, scale: float, subsampling: int) -> np.ndarray:
    """JPEG 재압축 차이를 증폭해 ELA uint8 배열을 반환함.

    ELA = clip(round(scale * abs(rgb - recompressed)), 0, 255).
    quality는 1~100, subsampling은 0(4:4:4), 1(4:2:2), 2(4:2:0)을 사용함.
    이미지별 최대값 정규화와 JPEG 증강은 하지 않음.
    """
    rgb = _validate_rgb(rgb)
    if isinstance(quality, bool) or not isinstance(quality, (int, np.integer)):
        raise ValueError("quality는 1~100의 정수여야 함.")
    if not 1 <= quality <= 100:
        raise ValueError("quality는 1~100의 정수여야 함.")
    if isinstance(subsampling, (bool, np.bool_)) or subsampling not in (0, 1, 2):
        raise ValueError("subsampling은 정수 0, 1, 2 중 하나여야 함.")
    if not isinstance(subsampling, (int, np.integer)):
        raise ValueError("subsampling은 정수여야 함.")
    if not np.isscalar(scale) or not np.isfinite(scale) or scale <= 0:
        raise ValueError("scale은 유한한 양수여야 함.")
    with BytesIO() as buffer:
        Image.fromarray(rgb).save(buffer, format="JPEG", quality=int(quality),
                                  subsampling=int(subsampling), optimize=False, progressive=False)
        buffer.seek(0)
        with Image.open(buffer) as image:
            recompressed = np.array(image.convert("RGB"), dtype=np.uint8)
    # uint8 뺄셈의 언더플로를 피하도록 실수로 변환함.
    difference = np.abs(rgb.astype(np.float64) - recompressed.astype(np.float64))
    # 큰 배율에서 곱셈이 넘치지 않도록 클리핑될 차이를 미리 제한함.
    if scale > 1:
        difference = np.minimum(difference, 255.0 / scale)
    return np.clip(np.rint(difference * scale), 0, 255).astype(np.uint8)
