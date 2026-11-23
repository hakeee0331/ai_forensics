# CAT-Net 전이학습·파인튜닝 실행 안내

2026-11-22 기준 005·006의 A100 학습·체크포인트 저장/재로드·각 2,257장 평가와 그림 13개씩의 저장 출력 검토를 마침. 005는 epoch 15, 006은 학습 개선 없이 epoch 0을 선택함. Drive 체크포인트 보관과 팀원 시각 검토 확인은 남아 있음. 확정 노트북은 보존하고 다음 실행은 새 개인 번호로 복사해 진행함. 기존 [004 평가](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md)는 사전학습 기준 결과로 보존함.

## 두 실험의 차이

| 실험 | 노트북 | 학습 범위 | 보고서 |
| --- | --- | --- | --- |
| 005 출력부 전이학습 | [005 노트북](../notebooks/catnet/EXP_kimjaehak_005_catnet_transfer_learning.ipynb) | 공식 `last_layer` 전체만 학습. RGB·DCT 특징 추출부와 융합부 고정 | [005 보고서](catnet/EXP_kimjaehak_005_catnet_transfer_learning.md) |
| 006 전체 파인튜닝 | [006 노트북](../notebooks/catnet/EXP_kimjaehak_006_catnet_finetuning.ipynb) | 전체 파라미터 학습. BatchNorm affine 파라미터 포함 | [006 보고서](catnet/EXP_kimjaehak_006_catnet_finetuning.md) |

두 노트북은 같은 `CAT_full_v2.pth.tar`에서 독립적으로 시작함. 006이 005 체크포인트에서 이어서 학습하지 않음. 출력 클래스가 같으므로 기존 출력부 가중치도 유지하며 재초기화하지 않음. 넓은 의미에서 파인튜닝도 전이학습이지만 여기서는 학습 범위로 이름을 구분함.

두 실험 모두 BatchNorm running mean/variance는 고정함. 작은 배치에서 통계 변경의 영향을 줄이기 위한 이번 비교 조건임. 파라미터의 gradient 허용과 BatchNorm 통계 갱신은 별개임. [공식 출력부 구조](https://github.com/mjkwon2021/CAT-Net/blob/5eb85900b0e72423c95a8d41bc835b86c8671f8a/lib/models/network_CAT.py) · [PyTorch 전이학습 안내](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html) · [BatchNorm 설명](https://docs.pytorch.org/docs/stable/generated/torch.nn.BatchNorm2d.html)

## 두 실험에서 사용한 설정

다음 값은 005·006에서 실제 사용한 설정임. 제안서의 BCE+Dice·Adam 1e-4 방향을 따르되 세부값은 아직 팀 공통 학습 규약으로 확정하지 않음. 변경이 필요하면 새 실험 번호에서 train·val로 조건을 검토하고 테스트 전에 고정함. 기존 두 노트북의 설정·출력은 수정하지 않음. T03·T05·T06·T19의 남은 팀 검토는 유지함.

| 항목 | 두 실험의 공통 설정 |
| --- | --- |
| 초기 모델 | 공식 커밋 `5eb85900b0e72423c95a8d41bc835b86c8671f8a`, CAT_full_v2 |
| 공통 코드 기준 | 프로젝트 `17fa55027c3d331979abf14a2039ad21e017dfb7`. 두 노트북은 그 이후 추가한 파일이며 자체 커밋을 소급해서 기록하지 않음 |
| 학습 데이터 | AutoSplice train: JPEG100 조작본 + 기존 정상 JPEG 원본. 각 파일을 epoch당 한 번 사용 |
| 검증 데이터 | AutoSplice val 전체, 원본 해상도. 정상·조작 모두 포함 |
| 학습 입력 | JPEG에서 RGB+DCT 구성 후 256×256 크롭. 시작 좌표는 16의 배수. 원본 안에서만 선택 |
| 증강 | 크롭 외 증강 없음. JPEG 증강·좌우반전·회전·리사이즈 없음 |
| 손실 | `BCEWithLogits(logit1 - logit0) + soft Dice`, 비중 1:1, 이미지별 평균 |
| 빈 학습 마스크 | 정상·빈 조작 크롭을 그대로 사용. Dice smooth=1이며 재추출하지 않음 |
| 최적화 | Adam, learning_rate=1e-4, weight_decay=0, 기본 betas·eps, 스케줄러 없음 |
| 학습량 | 배치 2, 최대 20 epoch, gradient 누적 없음, FP32 |
| 시드·순서 | seed 42. epoch별 고정 shuffle, 크롭은 seed·epoch·index로 따로 결정 |
| 선택 | 전체 val의 이미지별 BCE+Dice 평균 최소, patience 5. 동률은 먼저 나온 epoch 유지 |
| epoch 0 | 사전학습 모델의 val 평가도 후보에 포함. 개선이 없으면 epoch 0 선택 |
| 최종 평가 | 004와 같은 2,257장, 임계값 0.5, 조작 F1·IoU와 정상 픽셀 오탐률을 분리해 이미지별 평균 |
| CocoGlide 입력 | PNG→RGB JPEG100·4:4:4. 원본 PNG·마스크·크기 보존 |

정상·조작의 JPEG 저장 이력이 다르므로 이를 구분 단서로 학습할 가능성이 있음. 005·006은 기존 파일을 유지하며 이 영향을 제거한 실험이라고 주장하지 않음. 사전학습 데이터와 평가 데이터의 중복 가능성도 아직 검토가 필요함.

## 준비할 파일

1. [공통 실행 안내](workflow.md)에 따라 공유 `AI_Forensics` 바로가기를 MyDrive 최상위에 두고 VS Code의 Colab GPU 커널을 연결함.
2. 최신 로컬 `scripts/` 전체를 Drive의 `AI_Forensics/project/scripts/`에 업로드함. `__init__.py`, `catnet.py`, `datasets.py`, `preprocessing.py`, `evaluation.py`, `splits/autosplice_seed42.csv`가 필요함. 005·006은 공통 스크립트를 수정하지 않고 준비 기준 커밋의 코드를 사용함. 그 전처리 코드는 004 당시와 다름. 노트북 2절의 해시로 확인함.
3. Drive의 `AI_Forensics/project/models/pretrained/catnet/CAT_full_v2.pth.tar`와 데이터 ZIP 두 개를 확인함. [가중치 안내](../models/pretrained/README.md)의 기존 경로를 사용함.
4. 로컬에서 완료된 원본을 새 개인 번호로 복사해 출력·실행번호·메모를 비운 뒤 새 GPU 커널에 연결함. 독립 비교 실험도 별도 초기화한 커널에서 시작함. 노트북 자체를 Drive에 업로드할 필요는 없음.

```text
AI_Forensics/
├── datasets/
│   ├── AutoSplice/AutoSplice.zip
│   └── CocoGlide.zip
└── project/
    ├── scripts/                     # __init__.py·공통 모듈·splits 포함
    └── models/pretrained/catnet/CAT_full_v2.pth.tar
```

005·006의 추가 의존성은 004에서 기록된 버전으로 설치함. torch·torchvision과 NumPy·Pillow·pandas·matplotlib은 런타임 설치 상태를 출력함. Python 3.13.16·torch 2.14.1+cu130·torchvision 0.29.1+cu130·A100에서 설치·역전파·학습·재로드 동작을 확인함. 006은 최적화 불안정성이 나타났으므로 안정적인 파인튜닝 설정으로 확정하지 않음. 깨끗한 환경에서의 재현 설치와 팀 표준 버전 확정은 별도 작업임. 두 실험의 패키지·GPU와 공통 설정 서명을 대조하고 차이가 있으면 기록해야 함.

## 셀 실행 순서

| 노트북 절 | 수행할 일 | 다음 단계 전 확인 |
| --- | --- | --- |
| 1 | 추가 패키지 설치·환경 출력 | GPU=True, jpegio.read 확인, 버전·장치 기록. 설치가 재시작을 요구하면 커널 재시작 |
| 2~3 | Drive·코드·분할 해시 확인, 설정 출력 | import가 Drive의 scripts를 가리킴. 005·006의 공통 설정 서명 일치 |
| 4 | AutoSplice ZIP 준비·train/val 무결성 검사 | 원본 ID 1,818/227/228, split 중복 없음, 정상·조작 표본 존재 |
| 5 | 모델 로드·학습 범위 설정 | 동일 공식 커밋·가중치. 005는 last_layer만, 006은 전체 파라미터 학습 |
| 6 | 학습 크롭 시각화 | RGB와 마스크 위치가 맞고 입력 24×256×256, qtable 1×8×8 |
| 7 | 손실·검증 함수와 train 두 장의 3-step 점검 | 유한한 loss·gradient, 학습 가중치 갱신, 고정 파라미터·BN 통계 불변, 초기 가중치 복원 완료 |
| 8 | 본 학습·매 epoch val 평가 | epoch별 loss/F1/IoU/FPR, 선택 epoch, 시간과 메모리 출력 |
| 9 | 최선 체크포인트 재로드 | 저장 전후 val 표본 예측 대조 통과, 선택 epoch·해시 출력. 이 시점에 노트북 출력 저장 |
| 10~11 | test 목록·CocoGlide 변환·평가 | 변환 1,024장, 전체 2,257장, 6집단 표와 이미지별 전체 지표 출력 |
| 12 | 각 집단 2장씩 시각화 | 총 12개 그림, 시각화와 최초 평가 TP·FP·FN·TN 일치 |
| 마지막 | 체크포인트 Drive 복사·메모 작성·노트북 저장 | Drive 파일·해시 확인, 출력 포함 저장, 첫 셀 상태·실행일·사람 검토 메모 갱신 |

7절까지 먼저 실행해 동작과 그림을 확인한 후 본 학습으로 넘어감. 3-step 점검의 손실이 내려갔다고 성능 개선이나 전체 학습 성공으로 기록하지 않음. 본 학습에서 사용한 최종 설정을 변경한 뒤 이전 셀 출력과 섞지 않음.

후속 비교 실험도 설정을 먼저 고정함. 한 실험의 테스트 점수를 보고 다른 실험의 학습률·학습량·입력 조건을 고르지 않음. val 손실로 모델 선택을 마친 후 test를 평가함. 보고서에 남길 전체 이미지별 표는 노트북 출력으로 보관하며 별도 지표 JSON 구조는 추가하지 않음.

## 체크포인트 보관·재시작

005·006의 학습 중 저장 위치는 런타임의 `/content/checkpoints/<실험파일명>_best.pt`임. 실행 후 다음 Drive 경로에 복사해 보관함. 공식 초기 가중치와 실험에서 선택한 가중치를 구분함.

```text
AI_Forensics/project/models/
├── pretrained/catnet/
│   └── CAT_full_v2.pth.tar
└── checkpoints/catnet/
    ├── EXP_kimjaehak_005_catnet_transfer_learning_best.pt
    └── EXP_kimjaehak_006_catnet_finetuning_best.pt
```

| 실험 | 선택 epoch·의미 | 체크포인트 SHA-256 |
| --- | --- | --- |
| 005 | 15, 출력부를 학습한 모델 | `0162d5b9e6b606820db14910cf2740e526c042b6118b70c1a2d7de7b3787075e` |
| 006 | 0, 학습 전 사전학습 모델 | `b378861f61ee856e638c3ead2313c38b9d1aceaf2e3f7a3227b9623b97e14365` |

두 파일은 런타임 저장·재로드 최대 오차 0.0까지 확인함. 2026-11-23 기준 작성자가 Drive 미업로드 상태라고 확인함. 006은 학습 후 개선이 없어 초기 모델을 선택한 파일이며 성공한 파인튜닝 모델로 표시하지 않음. 메타데이터·파일 형식이 포함되므로 공식 초기 가중치와 파일 해시가 다르다는 사실이 학습된 가중치의 선택을 뜻하지 않음.

새 CAT-Net 학습 노트북은 val 기준으로 최선 체크포인트가 선택될 때마다 같은 Drive 폴더에 자동 보관함. 아래 복사 절차는 005·006의 기존 파일을 수동으로 보관할 때 사용함. [자동 보관 절차](workflow.md#새-학습-노트북의-자동-보관)를 따름.

### Drive에 복사

**런타임이 삭제되면 임시 체크포인트도 사라짐. 노트북 저장은 모델 파일 보관을 대신하지 않음.** VS Code에서 `files.download()` 셀이 실행돼도 실제 다운로드 파일을 확인해야 함. Drive 복사는 해당 런타임에 연결한 별도 임시 노트북에서 아래 셀만 실행할 수 있음. 학습 셀을 다시 실행하지 않음. Drive가 아직 마운트되지 않았다면 기존 마운트 절차부터 진행함.

`source`는 보관할 실험에 맞게 변경함. 005·006이 서로 다른 런타임에 있다면 각 런타임에서 해당 파일을 복사함. 해시는 위 표의 해당 값과도 대조함.

```python
from pathlib import Path
import hashlib
import shutil

def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

source = Path("/content/checkpoints/EXP_kimjaehak_005_catnet_transfer_learning_best.pt")
expected_hash = "0162d5b9e6b606820db14910cf2740e526c042b6118b70c1a2d7de7b3787075e"
drive_root = Path("/content/drive/MyDrive")
if not source.is_file():
    raise FileNotFoundError(f"런타임 체크포인트를 확인해야 함: {source}")
if not drive_root.is_dir():
    raise FileNotFoundError("Google Drive를 먼저 마운트해야 함.")
if file_sha256(source) != expected_hash:
    raise ValueError("보고서의 체크포인트 해시와 일치해야 함.")

save_dir = drive_root / "AI_Forensics/project/models/checkpoints/catnet"
save_dir.mkdir(parents=True, exist_ok=True)
destination = save_dir / source.name
if destination.exists():
    if file_sha256(destination) != expected_hash:
        raise FileExistsError("Drive에 내용이 다른 동명 파일이 있음. 저장 위치를 확인해야 함.")
else:
    shutil.copy2(source, destination)
if file_sha256(destination) != expected_hash:
    raise RuntimeError("복사 전후 해시가 다름. 파일을 다시 확인해야 함.")
print("Drive 보관 확인:", destination)
print("파일 크기:", destination.stat().st_size)
print("SHA-256:", expected_hash)
```

공유 폴더에는 쓰기 권한이 필요함. 파일명은 바꾸지 않고 실험 번호로 구분하며 내용이 다른 동명 파일을 덮어쓰지 않음. 복사 중 실패해 불완전한 파일이 남았다면 원본을 유지한 상태에서 대상 파일과 해시를 점검함. 보관 확인 출력·날짜를 개별 보고서에 추가하고 필요하면 Drive 웹에서 로컬로 다운로드함. 로컬에도 보관할 때 같은 상대 경로를 사용할 수 있으며 `.pt`는 기존 `.gitignore`로 제외됨. 가중치는 Git에 커밋하지 않음. 예측 이미지·지표 JSON의 저장 구조는 이번 경로와 별개로 미정임.

### 파일 내용과 재로드

체크포인트에는 모델 `state_dict`, 실험명·학습 범위·선택 epoch·val 지표, 환경·최종 설정·공통 코드 해시·공식 커밋·초기 가중치 해시, 선택 시점까지의 학습 이력과 재로드 대조용 val 예측이 들어 있음. 005의 epoch 16~20, 006의 epoch 1~5 이력은 best 파일에 없으므로 전체 학습 이력은 노트북 출력으로 보관함. optimizer·난수 상태가 없어 정확한 학습 재개 기능은 제공하지 않음.

학습 가중치를 `CatNetDetector.from_pretrained`에 직접 넣으면 공식 가중치 해시 검사에서 거부됨. 새 런타임에서는 패키지·공통 코드·공식 커밋을 맞추고, [공통 함수 안내](catnet.md)에 따라 공식 초기 가중치로 `detector`를 준비한 뒤 보관한 체크포인트의 `state_dict`를 덮어 로드함. 다음은 005 예시이며 006은 실험명·선택 epoch·해시를 위 표에 맞춰 변경함. `file_sha256`은 앞 절 함수를 사용함.

```python
import torch

experiment_id = "EXP_kimjaehak_005_catnet_transfer_learning"
source = Path("/content/drive/MyDrive/AI_Forensics/project/models/checkpoints/catnet") / f"{experiment_id}_best.pt"
expected_hash = "0162d5b9e6b606820db14910cf2740e526c042b6118b70c1a2d7de7b3787075e"
if file_sha256(source) != expected_hash:
    raise ValueError("체크포인트 해시를 확인해야 함.")
checkpoint = torch.load(source, map_location="cpu", weights_only=True)
if checkpoint["experiment_id"] != experiment_id or checkpoint["epoch"] != 15:
    raise ValueError("실험명과 선택 epoch를 확인해야 함.")
if checkpoint["official_commit"] != catnet.CODE_COMMIT:
    raise ValueError("체크포인트와 공식 코드 버전이 같아야 함.")
detector.model.load_state_dict(checkpoint["state_dict"], strict=True)
detector.model.eval()
print("로드한 실험:", checkpoint["experiment_id"], "선택 epoch:", checkpoint["epoch"])
```

005·006의 9절은 같은 런타임에서 저장 전후 val 예측 일치를 검증함. 위 Drive 보관본의 새 런타임 재로드는 아직 미실행임. 다른 GPU·환경에서는 비트 단위 동일성을 보장하지 않으므로 기준 val 표본의 예측도 대조하고 실제 환경·오차를 기록함.

학습 중에는 최선 파일을 임시 파일로 저장한 뒤 교체함. 본 학습 셀은 같은 이름의 파일이 있으면 중단하며 자동 덮어쓰기·이어 학습을 하지 않음. 실행이 중단되면 기존 출력과 가중치를 먼저 보관하고, 재실험은 새 번호로 진행함.

## CAT-Net 고유 처리와 한계

- U-Net의 ELA·32배수 제로 패딩을 CAT-Net 입력에 대신 적용하지 않음. CAT-Net은 공식 JPEG 로더의 8배수 패딩과 양자화 테이블을 유지함. 학습 크롭은 원본 안에서만 선택하고, val/test는 원본 부분만 loss·지표에 포함함.
- DCT 입력의 시작 좌표는 JPEG 블록과 맞춰야 함. 005·006의 16배수 크롭은 이 조건을 만족하지만 RGB와 DCT volume을 단순히 함께 뒤집는 증강은 구현하지 않음. [공식 입력 로더](https://github.com/mjkwon2021/CAT-Net/blob/5eb85900b0e72423c95a8d41bc835b86c8671f8a/Splicing/data/AbstractDataset.py)
- 학습용 BCE는 sigmoid를 먼저 계산하지 않고 두 logit 차이를 받음. Dice만 확률을 사용함. [BCEWithLogits 설명](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html)
- CUDA bilinear 보간의 역전파는 결정적 구현이 없을 수 있어 `torch.use_deterministic_algorithms(True, warn_only=True)`로 경고를 보존함. 시드·순서를 맞춰도 장치·연산에 따른 비트 단위 재현을 보장하지 않음. [PyTorch 재현 설정](https://docs.pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html)
- PNG→JPEG는 공식 비 JPEG 처리와 맞지만 픽셀·압축 단서를 바꿀 수 있음. CocoGlide의 낮은 점수를 변환 때문이라고 단정하거나 테스트 점수로 변환 품질을 고르지 않음. [004 분석](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md#png--jpeg-변환의-한계)

## 확인 결과와 남은 작업

005·006은 각각 코드 셀 15개·오류 출력 0개·PNG 13개를 확인함. 실제 패키지·GPU·공통 코드 및 분할 해시·학습 범위·3-step 갱신·학습 이력·체크포인트 재로드·테스트 집계·시각화를 대조함. 저장된 2,257행 혼동행렬에서 계산한 평균과 노트북의 요약 표가 일치함. 세부 수치와 해석은 개별 보고서·[결과 목록](results.md)에 기록함.

005는 JPEG100 개선과 함께 JPEG75·CocoGlide 일반화 악화가 나타남. 006은 첫 epoch 평균 train loss가 22,663.437917로 급증하고 epoch 1~5의 val F1·IoU가 0이 됨. val loss가 개선되지 않아 epoch 0을 선택함. 유한성 검사 통과가 안정적인 학습을 보장하지 않으며 현재 gradient 검사는 `max_norm=inf`라 큰 유한 gradient를 제한하지 않음. 후속 실험은 train·val에서 배치별 loss·logit·gradient부터 점검하고 학습률·갱신 범위의 영향을 검토함. 테스트로 조건을 고르지 않음.

체크포인트 Drive 보관·팀원 마스크 및 예측 검토 확인, 깨끗한 환경에서의 재현 설치, 사전학습 데이터 중복 검토와 T03·T05·T06·T19의 최종 합의는 남아 있음. 원본 노트북 첫 상태·사람 검토 메모에는 준비 시 문구가 남아 있으므로 실제 상태는 보고서·TODO를 기준으로 확인함. 원본을 수정하거나 출력을 다시 생성하지 않음.
