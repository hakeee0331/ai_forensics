# CAT-Net 공통 함수 사용 안내

[003 보고서](catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.md)의 모델 로드·단일 JPEG 추론 과정을 [scripts/catnet.py](../scripts/catnet.py)로 묶음. 공식 모델과 입력 로더를 그대로 사용하며, 003 노트북은 보존함.

공통 함수는 작성했으나 Colab에서의 실제 호출 검증은 아직 필요함. 004는 작성자가 직접 작성·실행하며, 보고서는 저장 출력을 확인한 뒤 작성함. 아래 코드는 새 노트북에 넣을 호출 예시임.

## 역할과 반환값

| 호출 | 처리 | 반환값 |
| --- | --- | --- |
| `prepare_code(code_dir)` | 공식 저장소 복제·003 커밋 고정. 기존 경로는 커밋·변경 파일·필수 파일 검사 | 공식 코드의 `Path` |
| `prepare_weights(source, destination)` | Drive 가중치 해시 확인·런타임 복사·복사본 검증. 같은 복사본은 재사용 | 가중치의 `Path` |
| `CatNetDetector.from_pretrained(code_dir, weight_path, device="cuda")` | 코드·가중치 확인, YAML 설정·모델 생성, 전체 가중치 strict 로드·장치 이동·평가 모드 설정 | 추론 객체 |
| `prepare_input(image_path, code_dir)` | 모델·가중치 로드 없이 공식 JPEG 입력 구성 | 배치 축 없는 CPU 텐서·양자화 테이블·원본 `(H, W)` |
| `detector.predict_proba(image_path)` | 공식 RGB·DCT·양자화 테이블 입력 구성, 추론, 원본 크기 복원 | `(H, W)` float32 NumPy 조작 확률 배열 |
| `detector.info` | 코드 커밋·가중치 해시와 크기·epoch·파라미터 수·장치·공통 함수 해시·복원 설정 | 기록용 딕셔너리 |

Drive 마운트·경로 설정·패키지 설치·데이터 준비 호출·임계값·평가·시각화는 노트북에 둠. 학습·파인튜닝·전체 데이터 평가 기능은 포함하지 않음. `detector.model`로 공식 PyTorch 모델을 확인할 수 있지만, 공통 추론 검증 중에는 가중치와 모델 설정을 변경하지 않음.

## 1. 패키지와 경로 준비

먼저 VS Code에서 새 노트북을 Colab GPU 커널에 연결함. 다음은 003에서 사용한 의존성의 설치 예시이며, 팀 공통 버전을 확정한 목록은 아님. `torch`·`torchvision`은 런타임 설치 상태와 CUDA 호환성을 먼저 확인함. 설치 패키지 이름은 `pyjpegio`, Python import 이름은 `jpegio`임.

```python
%pip install pyjpegio yacs PyYAML torch-dct opencv-python tqdm matplotlib
```

로컬 `scripts/`를 공유 Drive의 `AI_Forensics/project/scripts/`에 업로드함. 새 `catnet.py`와 기존 `__init__.py`, `datasets.py`, `preprocessing.py`, `evaluation.py`, 분할 CSV가 필요함. 이미 import한 코드를 교체했다면 커널을 재시작함.

```python
from pathlib import Path
from google.colab import drive
import sys

drive.mount("/content/drive")
project_root = Path("/content/drive/MyDrive/AI_Forensics/project")
code_dir = Path("/content/CAT-Net")
weight_source = project_root / "models/pretrained/catnet/CAT_full_v2.pth.tar"
weight_path = Path("/content/CAT_full_v2.pth.tar")

sys.path.insert(0, str(project_root))
from scripts import catnet, datasets, preprocessing, evaluation

for module in (catnet, datasets, preprocessing, evaluation):
    if Path(module.__file__).resolve().parent != (project_root / "scripts").resolve():
        raise RuntimeError("공통 코드 경로를 확인하고 커널을 재시작해야 함.")
    print(module.__file__, datasets.sha256(module.__file__))
```

출력한 해시를 실행 전에 검토한 로컬 파일 해시와 대조함. 새 `catnet.py`를 사용한다는 변경점과 실제 코드 버전도 노트북에 기록함. 이전 노트북의 기대 해시를 새 함수에 그대로 적용하지 않음. Python·실제 패키지 버전·CUDA·GPU 정보는 003의 환경 확인 셀을 참고해 출력함.

## 2. 공식 코드·가중치 준비와 모델 로드

```python
code_dir = catnet.prepare_code(code_dir)
weight_path = catnet.prepare_weights(weight_source, weight_path)
detector = catnet.CatNetDetector.from_pretrained(code_dir, weight_path, device="cuda")

for key, value in detector.info.items():
    print(f"{key}: {value}")
```

- 공식 코드 커밋은 `5eb85900b0e72423c95a8d41bc835b86c8671f8a`로 고정함. 새 경로일 때 공식 저장소만 복제하며, 프로젝트 저장소의 브랜치·커밋은 조작하지 않음. 기존 코드 경로가 다른 커밋이거나 변경된 상태라면 자동으로 덮어쓰지 않고 오류를 냄.
- 가중치는 003의 `CAT_full_v2.pth.tar`, SHA-256 `f82aaafdd1142775231feedcea0bb7027f7370561d9e8d107465454001865989`를 사용함. Drive 원본을 매번 검사하고, 런타임 복사본도 해시가 같을 때만 재사용함. 복사 도중 실패하면 기존 복사본은 보존함.
- `experiments/CAT_full.yaml`로 모델을 만들고 `state_dict`를 `strict=True`로 로드함. 이 전체 체크포인트는 003처럼 `weights_only=False`로 읽으므로 알려진 가중치 해시를 먼저 검사함. 누락된 키·다른 구조는 오류로 처리함.
- CUDA가 없으면 CPU로 자동 변경하지 않음. 오류를 확인하고 GPU 런타임을 선택함.

## 3. 데이터 준비와 한 장 추론

데이터 준비는 기존 `datasets.py`를 사용함. 003과 같은 AutoSplice JPEG100 train 표본을 사용하면 입력·결과를 비교하기 쉬움. 아래 셀은 앞의 준비 셀 다음에 실행함.

```python
archive_path = project_root.parent / "datasets/AutoSplice/AutoSplice.zip"
split_path = project_root / "scripts/splits/autosplice_seed42.csv"
data_root = Path("/content/datasets")
archive_hash = "0d94e2df6842f44c11e21ee207707c49fd9717ec89048bd6f28fc1e07c4a5e36"
split_hash = "f8a2893ab93b82264e6434fa0c26f09472de05bd98829065c2a0db846ace7b1e"

if datasets.sha256(split_path) != split_hash:
    raise ValueError("003에서 사용한 분할 CSV와 일치해야 함.")
print("분할 SHA-256:", datasets.sha256(split_path))
datasets.prepare_dataset_zip(archive_path, Path("/content/AutoSplice.zip"), data_root, archive_hash)
records = datasets.autosplice_records(data_root / "AutoSplice", split_path, quality=100)
sample = next(r for r in records if r["split"] == "train" and r["kind"] == "manipulated" and r["image_path"].name == "39406_0.jpg")
image_path, mask_path = sample["image_path"], sample["mask_path"]

probability = detector.predict_proba(image_path)
print("이미지:", image_path.name, "분할:", sample["split"])
print("조작 확률:", probability.shape, probability.dtype)
print("최솟값·최댓값:", float(probability.min()), float(probability.max()))
```

`predict_proba`는 파일 경로를 받음. RGB 배열만 전달하면 원본 JPEG의 DCT 계수·양자화 테이블을 읽을 수 없으므로 배열 입력은 지원하지 않음. `prepare_input()`에서 공식 로더의 `RGB`, `DCTvol`, `qtable` 입력을 구성하고, 출력 logits를 입력 크기로 bilinear 보간(`align_corners=False`)한 뒤 softmax의 조작 클래스 1을 선택하고 패딩을 제거함. 이 순서는 003과 같음.

현재는 **JPEG 한 장씩** 지원함. PNG를 임의의 품질로 재압축하지 않음. CocoGlide 등 비 JPEG 입력의 변환 조건, 정상 이미지·여러 해상도·전체 데이터 평가와 사전학습 데이터 중복 가능성은 별도로 검증해야 함.

## 입력 구성만 재사용할 때

학습용 Dataset에서는 추론 객체를 만들지 않고 입력 함수를 직접 호출할 수 있음. 먼저 패키지 설치와 `prepare_code(code_dir)`를 마쳐야 함. 가중치 파일이나 GPU는 입력 구성에 필요하지 않음.

```python
input_tensor, qtable, original_size = catnet.prepare_input(image_path, code_dir)

print("RGB+DCT:", input_tensor.shape, input_tensor.dtype)
print("양자화 테이블:", qtable.shape, qtable.dtype)
print("원본 (H, W):", original_size)
```

| 반환값 | 의미 |
| --- | --- |
| `input_tensor` | CPU float32 텐서 `(24, H_pad, W_pad)`. RGB 3채널과 DCT volume 21채널을 합친 입력임 |
| `qtable` | CPU float32 텐서 `(1, 8, 8)`. 첫 JPEG 성분의 양자화 테이블임 |
| `original_size` | 패딩 전 `(높이, 너비)` 튜플. 예측을 원본 크기로 복원할 때 사용함 |

배치 축 추가·GPU 이동·모델 호출은 이 함수에서 하지 않음. `inference_mode()`나 `no_grad()`로 학습 경로를 감싸지 않으며 모델의 train/eval 상태도 바꾸지 않음. 공식 로더가 반환하는 임시 마스크는 버리고, 실제 정답 마스크는 별도로 읽어야 함. `predict_proba()`도 이 함수를 호출하므로 추론과 학습 준비에 같은 입력 구성을 사용할 수 있음.

현재 함수는 JPEG 전체 이미지의 입력을 구성함. 서로 다른 크기의 텐서는 그대로 한 배치로 쌓을 수 없으므로 학습용 크롭·배치 정책을 따로 정해야 함. 마스크와 입력 위치를 맞추고 패딩 영역이 손실에 포함되지 않도록 처리해야 함. DCT와 RGB의 정합성·JPEG 블록 정렬을 유지해야 하므로 임의의 크롭·반전 증강을 이 함수에 추가하지 않음. 이러한 학습 전처리와 손실·optimizer·학습 반복문은 후속 파인튜닝 작업에서 구현·검증함.

입력용 공식 로더는 프로세스에서 처음 사용할 때 코드 커밋과 import 경로를 확인한 뒤 재사용함. 모델이나 이미지 텐서를 캐시하지 않음. 실행 중 공식 코드를 교체하지 않으며, 코드 변경 시 커널을 재시작해야 함. 학습한 가중치를 읽는 별도 로더는 아직 제공하지 않음.

## 4. 평가와 시각화

```python
import numpy as np
import matplotlib.pyplot as plt

threshold = 0.5
mask = preprocessing.load_binary_mask(mask_path, foreground_value=255)
prediction = (probability >= threshold).astype(np.uint8)
tp, fp, fn, tn = evaluation.confusion_counts(mask, prediction)
print("임계값:", threshold, "평가 크기:", mask.shape)
print("TP·FP·FN·TN:", tp, fp, fn, tn)
print("Pixel F1:", evaluation.pixel_f1(tp, fp, fn))
print("IoU:", evaluation.iou(tp, fp, fn))

rgb = preprocessing.load_rgb(image_path)
fig, axes = plt.subplots(1, 4, figsize=(16, 4), constrained_layout=True)
for ax, value, title in zip(axes, (rgb, mask, probability, prediction), ("RGB", "Ground truth", "Probability", "Prediction")):
    ax.imshow(value, vmin=0, vmax=1, cmap="viridis" if title == "Probability" else "gray")
    ax.set_title(title)
    ax.axis("off")
plt.show()
```

0.5는 003과 비교하기 위한 설정임. 팀 평가 규약의 최종 확정을 의미하지 않음. 003에서 같은 이미지의 TP·FP·FN·TN은 8,105·1,659·16·85,964, Pixel F1은 0.906346, IoU는 0.828732였음. 새 실행 결과는 실제 출력으로 기록하며 이전 점수를 복사하지 않음.

## 검증 범위와 후속 확인

2026-11-20에 합성 파일·대체 객체를 사용한 12개 검사로 가중치 복사·재사용·손상·중단 처리, 코드 커밋·변경·필수 파일 검사, import 충돌, strict 로드 호출, 보간→softmax→패딩 제거 순서와 PNG 거부를 확인함. 입력 함수의 텐서·원본 크기 반환, 배치·장치 변경 및 추론 모드 호출이 없는 점, 모델 생성 없이 입력 로더를 재사용하는 점도 검사함. 실제 공식 저장소 복제·체크포인트 역직렬화·JPEG 디코딩·GPU 추론·역전파는 이 검사에 포함하지 않음.

004에서는 새 커널에서 위 순서로 실행하고 경로·환경·해시·표본·점수·그림을 저장해야 함. 003은 확률 배열 자체를 저장하지 않았으므로 기존 점수 일치만으로 확률의 완전한 동일성을 입증할 수는 없음. 수치 대조가 필요하면 004에서 같은 모델·같은 입력으로 003의 입력·추론 코드를 직접 호출한 결과와 공통 함수 결과의 최대 절대 오차를 비교함. 이를 위해 003 원본을 재실행하지 않음.

공식 구조와 입력의 근거는 [CAT-Net 저장소](https://github.com/mjkwon2021/CAT-Net), 프로젝트에서 실제 사용한 조건과 결과의 근거는 [003 보고서](catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.md)와 연결된 저장 노트북임.
