# 전처리 함수 사용 안내

검토일: 2026-11-17. 대상: [scripts/preprocessing.py](../scripts/preprocessing.py).

검토한 코드 SHA-256: `69809276be12200a3cd2ef1e96364a7d168b39cae0a2cce1946f84d7ce74db07`. 이후 코드가 바뀌면 이 문서의 입력 조건과 검증 기록도 함께 확인해야 함.

현재 코드는 제안서의 전처리에 사용할 공통 함수 초안임. 정상 입력에서 RGB·마스크 읽기, 같은 위치 크롭, ELA 계산을 확인함. **팀원들의 검증이 아직 필요함.** 학습 전처리 전체나 팀 설정이 확정된 상태는 아님. 이 문서는 사용 안내이며 실험 성능 보고서가 아님.

## 제안서와 구현의 관계

`10조_Proposal.pdf` 2쪽 4-2절, 4-3절 및 3쪽 5.1절을 기준으로 대조함. 제안서의 계획과 현재 적용 범위는 아래처럼 구분함.

| 항목 | 제안서 내용 | 현재 구현·사용 조건 |
| --- | --- | --- |
| ELA | 원본과 JPEG 재압축본의 절대 차이에 배율을 곱함 | make_ela의 핵심 계산과 일치함 |
| ELA 설정 | Q′=75, α=15는 그림의 예시임 | quality·scale·subsampling을 호출할 때 전달함. 팀 기본값은 미확정임 |
| 출력 수치 형식 | 반올림·클리핑·자료형을 별도로 명시하지 않음 | 현재 구현은 반올림 후 0~255로 제한한 uint8임. 제안서에 추가된 구현 선택이며 기본 비교 전에 확인해야 함 |
| 학습 크롭 | 시작 좌표와 크기가 모두 16의 배수인 조각을 매 epoch 자름 | crop_pair는 지정한 영역만 자름. 좌표 선택·16의 배수 검사는 호출하는 쪽에서 처리해야 함 |
| 변환 순서 | 크롭한 뒤 ELA를 계산하고 RGB·ELA·마스크에 같은 무작위 좌우반전을 적용함 | 크롭·ELA 함수만 있음. 같은 반전 결정을 적용하는 학습 흐름은 아직 없음 |
| 리사이즈·회전 | 사용하지 않음 | 네 함수 모두 리사이즈·회전을 수행하지 않음. 이미지·마스크의 EXIF 방향 정합성은 별도 확인이 필요함 |
| 평가 | 원본 크기로 수행함 | load_rgb·load_binary_mask는 원본 크기를 유지함. 평가에서 학습용 크롭을 그대로 적용하지 않도록 해야 함 |
| JPEG 증강 | 크롭 RGB를 무작위 품질 70~100으로 재압축한 뒤 ELA를 계산함 | 기본 비교 이후로 보류함. make_ela의 내부 재압축은 증강이 아님 |
| CocoGlide 평가 | PNG를 JPEG 100·90·75로 변환해 평가함 | 별도 평가 데이터 준비가 필요함. 현재 예제의 PNG 로드는 해당 벤치마크를 구현한 것이 아님 |
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
- 정상 이미지에 마스크 파일이 없다면 `np.zeros(rgb.shape[:2], dtype=np.uint8)`로 구성함.
- 현재 foreground_value는 Python int를 요구함. NumPy 정수는 `int(value)`로 전달해야 함.

## crop_pair(rgb, mask, *, top, left, height, width)

이미지와 마스크를 같은 영역으로 잘라 두 배열을 반환함. top·left는 시작 행·열이며 0 이상, height·width는 높이·너비이며 양수여야 함. 네 값은 정수이고 크롭 영역은 원본 안에 있어야 함.

```python
rgb_crop, mask_crop = crop_pair(rgb, mask, top=top, left=left, height=height, width=width)
```

반환값은 복사본이므로 이후 수정해도 원본 배열을 바꾸지 않음. 좌표를 무작위로 선택하거나 부족한 크기를 패딩하지 않음. 제안서의 학습 조건에 맞추려면 top·left·height·width를 모두 16의 배수로 정해야 함. 원본이 크롭 크기보다 작을 때의 처리 방식은 아직 정하지 않음.

## make_ela(rgb, *, quality, scale, subsampling)

RGB를 메모리에서 JPEG로 저장한 뒤 다시 읽어 절대 차이를 계산함. 원본 파일을 덮어쓰지 않음.

```python
ela = make_ela(rgb, quality=ela_quality, scale=ela_scale, subsampling=jpeg_subsampling)
```

| 인자 | 의미·현재 조건 |
| --- | --- |
| quality | ELA 내부 재압축 품질임. 정수 1~100을 받음. 입력 이미지의 JPEG 품질과 별개임 |
| scale | 차이를 증폭할 유한한 양수임. Python int 또는 float로 전달하고 불리언·문자열·복소수는 사용하지 않음 |
| subsampling | 정수 0=4:4:4, 1=4:2:2, 2=4:2:0임 |

계산은 `clip(rint(scale * abs(rgb - recompressed)), 0, 255)`임. 차이를 구하기 전에 float64로 변환하므로 uint8 뺄셈의 언더플로를 피함. 큰 배율에서는 최종적으로 255가 될 차이를 미리 제한해 곱셈 오버플로를 방지함. 이 처리는 일반적인 입력에서 계산 오류로 확인되지 않았으며 단순화 후보임.

`np.rint`는 가장 가까운 정수로 반올림하고 정확히 중간인 값은 짝수 쪽을 택함. 예를 들어 2.5는 2, 3.5는 4가 됨. [NumPy 설명](https://numpy.org/doc/stable/reference/generated/numpy.rint.html)

JPEG 저장 옵션은 optimize=False, progressive=False로 고정함. 서브샘플링의 숫자 의미는 [Pillow 설명](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg)을 따름. Pillow와 JPEG 인코더 환경도 실행 기록에 남기는 것이 좋음.

## 노트북에서 연결하는 방법

현재 평가 함수 예제는 load_rgb·load_binary_mask만 사용함. 아래는 향후 학습 노트북에 연결할 순서를 보여주는 코드임. 경로·크롭 위치·크기·ELA 설정·반전 여부는 호출 전에 정해야 하며, 이 예시 자체를 실행하거나 팀 설정으로 확정하지 않음.

```python
from scripts.preprocessing import load_rgb, load_binary_mask, crop_pair, make_ela

rgb = load_rgb(image_path)
mask = load_binary_mask(mask_path, foreground_value=255)
assert rgb.shape[:2] == mask.shape
assert all(value % 16 == 0 for value in (top, left, height, width))
rgb, mask = crop_pair(rgb, mask, top=top, left=left, height=height, width=width)
ela = make_ela(rgb, quality=ela_quality, scale=ela_scale, subsampling=jpeg_subsampling)

if flip_horizontal:
    rgb = rgb[:, ::-1].copy()
    ela = ela[:, ::-1].copy()
    mask = mask[:, ::-1].copy()
```

flip_horizontal은 한 샘플에 대해 한 번만 정하고 세 배열에 같이 적용함. RGB를 먼저 반전한 뒤 ELA를 다시 계산하는 순서로 바꾸지 않음. 세 U-Net의 비교에서는 같은 데이터·크롭·변환 조건을 유지함. 원본 해상도 평가에서는 학습용 무작위 크롭·반전을 적용하지 않고 원본 RGB에서 ELA를 계산함.

## 확인된 한계와 검증 범위

2026-11-17 합성 이미지로 RGB·마스크 로드, 동일 위치 크롭, 크롭 복사본의 독립성을 확인함. ELA는 품질 1·75·100, 서브샘플링 0·1·2, 배율 0.5·15·1000의 27개 조합에서 별도로 재압축한 RGB로 직접 계산한 값과 일치함. 이 검사는 사용 중인 JPEG 인코더에 대한 함수 계산 검증이며, 제안서 그림 재현·모델 성능·Colab 검증이 아님.

다음 입력 검사 문제도 재현했으며 아직 수정하지 않음.

| 입력 | 현재 동작 | 검토 사항 |
| --- | --- | --- |
| scale=True | 배율 1처럼 허용함 | 실수 설정에서 불리언을 명시적으로 거부할 필요가 있음 |
| scale="15", scale=1+2j | TypeError 발생 | 허용 타입을 먼저 검사해 안내용 오류를 일관되게 처리할 필요가 있음 |
| foreground_value=np.int64(255) | ValueError 발생 | 다른 정수 인자와 NumPy 정수 허용 기준이 다름 |

정상 입력에서 검사한 계산은 통과했지만, 모든 입력과 제안서의 전체 학습 흐름에 오류가 없다고 확정한 것은 아님. ELA 반올림·클리핑·자료형, 공통 설정, 크롭 정책은 [TODO](../TODO.md)의 T06에서 계속 검토함. `_validate_rgb`, `_validate_mask`는 모듈 내부 검사 함수이며 노트북에서 직접 호출할 필요가 없음.

팀원들은 Colab에서 실제 데이터의 이미지·마스크 정합성, 동일 위치 크롭, ELA 계산 결과와 설정을 검증해야 함. 검증한 코드 버전·설정·출력을 노트북에 저장하고 확인 결과를 공유한 뒤 공통 전처리 규약을 확정함. 기존 합성 입력 검사는 팀원 검증 완료를 의미하지 않음.

## 수정한 코드 반영

공통 코드 변경 후에는 [README의 필수 업로드 절차](../README.md#공통-코드-수정-후-drive-업로드--필수)에 따라 Drive의 `AI_Forensics/project/scripts/`에도 반영해야 함. 현재 출력을 저장한 뒤 커널을 재시작하고 변경한 코드로 실행함. 노트북·보고서에는 실제 실행한 코드의 버전과 최종 설정을 기록함.
