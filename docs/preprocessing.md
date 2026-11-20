# 전처리 함수 사용 안내

갱신일: 2026-11-20. 대상: [scripts/preprocessing.py](../scripts/preprocessing.py).

대상 코드 SHA-256: `73ce7fa0aee3f2b901a9ab04d430ff8ae2bcaa7262005600f6b08f04b95c652f`. 이후 코드가 바뀌면 이 문서의 입력 조건과 검증 기록도 함께 확인해야 함.

현재 코드는 제안서의 전처리에 사용할 공통 함수이며, 팀 합의로 확정한 ELA 설정(quality=90, scale=15, subsampling=2), 전처리 순서(원본 ELA 선계산 → 크롭 → 좌우반전), 학습 크롭(256×256), 평가용 우하단 제로 패딩(32의 배수)·언패딩 기준을 반영함. 이 문서는 사용 안내이며 실험 성능 보고서가 아님.

## 제안서와 구현의 관계

`10조_Proposal.pdf` 2쪽 4-2절, 4-3절 및 3쪽 5.1절을 기준으로 대조함. 제안서의 계획과 팀 합의로 확정한 적용 범위는 아래처럼 구분함.

| 항목 | 제안서 내용 | 현재 구현·팀 합의 조건 |
| --- | --- | --- |
| ELA | 원본과 JPEG 재압축본의 절대 차이에 배율을 곱함 | make_ela의 핵심 계산과 일치함 |
| ELA 설정 | Q′=75, α=15는 그림의 예시임 | 팀 합의로 quality=90, scale=15, subsampling=2를 기본 비교 기준으로 확정함. 함수에는 명시적으로 전달함 |
| 출력 수치 형식 | 반올림·클리핑·자료형을 별도로 명시하지 않음 | 반올림 후 0~255로 제한한 uint8을 사용함 |
| 학습 크롭 | 시작 좌표와 크기가 모두 16의 배수인 조각을 매 epoch 자름 | 학습 크롭 크기를 256×256으로 확정함. crop_pair는 지정한 영역만 자르며 좌표 선택은 호출하는 쪽에서 처리함 |
| 변환 순서 | 크롭한 뒤 ELA를 계산하고 RGB·ELA·마스크에 같은 무작위 좌우반전을 적용함 | JPEG 블록 격자 보존을 위해 원본 이미지에서 ELA를 먼저 계산한 뒤, 동일 위치 크롭과 무작위 좌우반전을 적용하는 순서로 확정함 |
| 리사이즈·회전 | 사용하지 않음 | 모든 함수가 리사이즈·회전을 수행하지 않음 |
| 평가 해상도·패딩 | 원본 크기로 수행함 | 추론 시 pad_image로 좌측 상단 (0, 0)을 고정한 채 32의 배수로 우하단 제로 패딩하고, 출력 후 unpad_image로 원본 크기로 복원해 원본 마스크와 비교함 |
| JPEG 증강 | 크롭 RGB를 무작위 품질 70~100으로 재압축한 뒤 ELA를 계산함 | 기본 비교 이후(T14)로 보류함. make_ela의 내부 재압축은 증강이 아님 |
| CocoGlide 평가 | PNG를 JPEG 100·90·75로 변환해 평가함 | 외부 테스트용으로 유지함 |
| CAT-Net | RGB·DCT 계수·양자화 테이블을 입력으로 사용함 | 이 모듈로 CAT-Net 전용 입력 처리를 대체하지 않음 |

## 공통 입력·출력

- RGB: `(H, W, 3)` 순서, `uint8`, 값 범위 0~255임. 채널 순서는 RGB임.
- 이진 마스크: `(H, W)`, `uint8`, 정상 0·조작 1임.
- ELA: 입력과 같은 `(H, W, 3)` 크기의 `uint8` 배열임. 채널 평균이나 이미지별 최대값 정규화는 하지 않음.
- 0~1 정규화·모델별 정규화·텐서 변환·채널 축 이동·RGB+ELA 결합은 노트북에서 처리함.

## load_rgb(path)

이미지 파일을 열고 RGB 3채널 배열을 반환함. 입력 경로는 문자열 또는 Path를 사용함. 크기 변경이나 EXIF 방향 자동 회전은 하지 않음. 파일 누락·손상 오류는 Pillow에서 발생함.

```python
rgb = load_rgb(image_path)
```

일반적인 RGB 이미지용임. 투명 채널이나 다른 색 모드의 의미까지 보존하는 로더는 아니므로 새 데이터셋을 추가할 때 원본 모드를 확인해야 함.

## load_binary_mask(path, *, foreground_value)

배경값 0과 지정한 전경값으로 구성된 2차원 마스크를 읽어 0/1로 반환함. foreground_value는 이름을 붙여 반드시 전달함. 현재 데이터 점검에서 AutoSplice·CocoGlide 마스크는 단일 채널의 0/255 값으로 확인했으므로 255를 사용함.

```python
mask = load_binary_mask(mask_path, foreground_value=255)
assert rgb.shape[:2] == mask.shape
```

- 전경값 외의 양수를 모두 조작으로 처리하지 않음. 예상하지 않은 값이 있으면 오류가 발생함.
- RGB 컬러 마스크는 자동으로 회색조 변환하지 않고 거부함.
- 전부 0인 마스크도 허용함. 원본 마스크 파일은 변경하지 않음.
- 정상 이미지에 마스크 파일이 없다면 np.zeros(rgb.shape[:2], dtype=np.uint8)로 구성함.
- foreground_value는 Python int와 NumPy 정수(np.integer)를 모두 허용하며, 불리언은 거부함.

## crop_pair(rgb, mask, *, top, left, height, width)

이미지와 마스크를 같은 영역으로 잘라 두 배열을 반환함. top·left는 시작 행·열이며 0 이상, height·width는 높이·너비이며 양수여야 함. 네 값은 정수이고 크롭 영역은 원본 안에 있어야 함.

```python
rgb_crop, mask_crop = crop_pair(rgb, mask, top=top, left=left, height=height, width=width)
```

반환값은 복사본이므로 이후 수정해도 원본 배열을 바꾸지 않음. 좌표를 무작위로 선택하거나 부족한 크기를 패딩하지 않음. 학습 시 크롭 크기는 256×256으로 통일하며, 좌표는 16의 배수로 선택함.

## make_ela(rgb, *, quality, scale, subsampling)

RGB를 메모리에서 JPEG로 저장한 뒤 다시 읽어 절대 차이를 계산함. 원본 파일을 덮어쓰지 않음.

```python
ela = make_ela(rgb, quality=90, scale=15, subsampling=2)
```

| 인자 | 의미·현재 조건 |
| --- | --- |
| quality | ELA 내부 재압축 품질임. 정수 1~100을 받음. 기본 비교에서는 90을 사용함 |
| scale | 차이를 증폭할 유한한 양의 실수임. 불리언·문자열·복소수는 거부함. 기본 비교에서는 15를 사용함 |
| subsampling | 정수 0=4:4:4, 1=4:2:2, 2=4:2:0임. 기본 비교에서는 2를 사용함 |

계산은 `clip(rint(scale * abs(rgb - recompressed)), 0, 255)`임. 차이를 구하기 전에 float64로 변환하므로 uint8 뺄셈의 언더플로를 피함. 큰 배율에서는 최종적으로 255가 될 차이를 미리 제한해 곱셈 오버플로를 방지함.

`np.rint`는 가장 가까운 정수로 반올림하고 정확히 중간인 값은 짝수 쪽을 택함. 예를 들어 2.5는 2, 3.5는 4가 됨. [NumPy 설명](https://numpy.org/doc/stable/reference/generated/numpy.rint.html)

JPEG 저장 옵션은 optimize=False, progressive=False로 고정함. 서브샘플링의 숫자 의미는 [Pillow 설명](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg)을 따름. Pillow와 JPEG 인코더 환경도 실행 기록에 남기는 것이 좋음.

## pad_image(array, *, multiple=32) 및 unpad_image(array, *, original_size)

평가(Validation·Test) 시 U-Net의 다운샘플링·업샘플링 배수 조건(32의 배수)을 맞추기 위해 입력 배열의 우하단에 0 패딩을 추가하고, 추론 후 원본 해상도로 패딩을 제거함. 좌측 상단 (0, 0)을 고정하므로 오프셋 계산 없이 원본 크기로 잘라낼 수 있음.

```python
padded_rgb, orig_size = pad_image(rgb, multiple=32)
# 모델 추론 후 출력 확률맵에서 패딩 제거
pred_prob = unpad_image(pred_prob_padded, original_size=orig_size)
```

- pad_image는 (H, W) 또는 (H, W, C) 배열을 받아 (패딩된 배열, (원본 높이, 원본 너비))를 반환함. 이미 multiple의 배수라면 복사본과 원본 크기를 반환함.
- unpad_image는 패딩된 예측 배열과 original_size=(orig_h, orig_w)를 받아 [:orig_h, :orig_w] 영역의 복사본을 반환함. 정답 마스크는 패딩하지 않고 unpad_image 결과와 원본 마스크를 직접 비교함.

## 노트북에서 연결하는 방법

### 1. 학습(Train) 전처리 순서

원본 이미지에서 ELA를 먼저 계산한 뒤, 동일한 위치로 256×256 크롭하고 같은 무작위 좌우반전을 적용함.

```python
from scripts.preprocessing import load_rgb, load_binary_mask, make_ela, crop_pair

rgb = load_rgb(image_path)
mask = load_binary_mask(mask_path, foreground_value=255)
ela = make_ela(rgb, quality=90, scale=15, subsampling=2)

rgb, mask = crop_pair(rgb, mask, top=top, left=left, height=256, width=256)
ela = ela[top:top + 256, left:left + 256].copy()

if flip_horizontal:
    rgb = rgb[:, ::-1].copy()
    ela = ela[:, ::-1].copy()
    mask = mask[:, ::-1].copy()
```
flip_horizontal은 한 샘플에 대해 한 번만 정하고 세 배열에 같이 적용함. RGB를 먼저 반전한 뒤 ELA를 다시 계산하는 순서로 바꾸지 않음. 세 U-Net의 비교에서는 같은 데이터·크롭·변환 조건을 유지함.

### 2. 평가(Validation·Test) 전처리·후처리 순서

학습용 크롭과 좌우반전을 적용하지 않고 원본 해상도에서 ELA를 계산한 뒤, 모델 입력 직전에 우하단 패딩을 적용하고 추론 후 언패딩해 원본 마스크와 평가함.

```python
from scripts.preprocessing import load_rgb, load_binary_mask, make_ela, pad_image, unpad_image

rgb = load_rgb(image_path)
mask = load_binary_mask(mask_path, foreground_value=255)
ela = make_ela(rgb, quality=90, scale=15, subsampling=2)

padded_rgb, orig_size = pad_image(rgb, multiple=32)
padded_ela, _ = pad_image(ela, multiple=32)

# padded_rgb(및 padded_ela)로 모델 추론 후 (H_pad, W_pad) 확률맵 획득
pred_prob = unpad_image(pred_prob_padded, original_size=orig_size)
```

## 확인된 한계와 검증 범위

2026-11-17 합성 이미지로 RGB·마스크 로드, 동일 위치 크롭, 크롭 복사본의 독립성을 확인함. ELA는 품질 1·75·100, 서브샘플링 0·1·2, 배율 0.5·15·1000의 27개 조합에서 별도로 재압축한 RGB로 직접 계산한 값과 일치함. 이 검사는 사용 중인 JPEG 인코더에 대한 함수 계산 검증이며, 제안서 그림 재현·모델 성능·Colab 검증이 아님.

2026-11-20 기존에 재현했던 다음 입력 검사 문제를 모두 수정하고, 평가용 우하단 제로 패딩·언패딩(pad_image, unpad_image) 함수를 추가해 합성 배열에서 동작을 확인함.

| 입력 | 이전 동작 | 수정 후 동작 |
| --- | --- | --- |
| scale=True | 배율 1처럼 허용함 | ValueError를 발생시켜 불리언을 거부함 |
| scale="15", scale=1+2j | TypeError 발생 | 허용 타입을 먼저 검사해 일관되게 ValueError를 발생시킴 |
| foreground_value=np.int64(255) | ValueError 발생 | 다른 정수 인자와 동일하게 NumPy 정수를 허용함 |

정상 입력에서 검사한 계산은 통과했지만, 모든 입력과 제안서의 전체 학습 흐름에 오류가 없다고 확정한 것은 아님. 나머지 평가 집계·임계값·학습 조건은 [TODO](../TODO.md)의 T06에서 계속 검토함. _validate_rgb, _validate_mask는 모듈 내부 검사 함수이며 노트북에서 직접 호출할 필요가 없음.

팀원들은 Colab에서 실제 데이터의 이미지·마스크 정합성, 동일 위치 크롭, ELA 계산 결과와 설정을 검증해야 함. 검증한 코드 버전·설정·출력을 노트북에 저장하고 확인 결과를 공유한 뒤 공통 전처리 규약을 확정함. 기존 합성 입력 검사는 팀원 검증 완료를 의미하지 않음.

## 수정한 코드 반영

공통 코드 변경 후에는 [README의 필수 업로드 절차](../README.md#공통-코드-수정-후-drive-업로드--필수)에 따라 Drive의 AI_Forensics/project/scripts/에도 반영해야 함. 현재 출력을 저장한 뒤 커널을 재시작하고 변경한 코드로 실행함. 노트북·보고서에는 실제 실행한 코드의 버전과 최종 설정을 기록함.