# AI 인페인팅 영역 검출

AI로 이미지의 일부를 바꾼 영역을 픽셀 단위로 찾아내는 프로젝트다. RGB, ELA, RGB+ELA 입력을 사용하는 U-Net을 비교하고, 사전 학습된 CAT-Net의 결과도 함께 분석한다.

## 처음 참여할 때

001 평가 함수 예제, 002 데이터 EDA, 003 CAT-Net 단일 이미지 확인과 004 CAT-Net 전체 테스트 평가의 저장 출력 검토를 마쳤다. 004에서 AutoSplice test·CocoGlide 전체 2,257장과 시각화 18개를 확인했다. U-Net의 작은 배치 학습 동작 확인은 완료했으며, CAT-Net의 005·006 학습·평가도 출력 검토를 마쳤다. 세 U-Net의 본격적인 비교 실험은 아직 진행하지 않았다. T05에서 기존 분할 유지를 확정했다. 학습 환경과 공통 비교 조건은 TODO에서 확인한다. 현재 진행 상태는 [TODO](TODO.md), 실제 측정 결과는 [결과 목록과 개별 보고서](docs/results.md)를 기준으로 확인한다.

| 문서 | 확인할 내용 |
| --- | --- |
| [CONTRIBUTING](CONTRIBUTING.md) | 작성자별 파일명·번호, 노트북 보존, 보고·Git 규칙 |
| [노트북 실행과 결과 전달](docs/workflow.md) | 새 파일 준비 → Drive 업로드 → VS Code·Colab 연결 → 실행·저장 → 보고서 갱신 |
| [전처리 함수 사용 안내](docs/preprocessing.md) | 공통 함수의 입력·출력·제약과 팀원 검증 항목 |
| [CAT-Net 공통 함수](docs/catnet.md) | 공식 코드·가중치 준비, 모델 로드·JPEG 추론 호출 예시 |
| [CAT-Net 학습 실행 안내](docs/catnet_training.md) | 005·006 실제 결과, 후속 실행·체크포인트 Drive 보관·결과 전달 |
| [패키지 사용 제안](docs/package_proposal.md) | 학습 패키지 구성안. 아직 팀 합의·버전 확정 전임 |
| [AGENTS](AGENTS.md) | 에이전트의 작업 범위와 결과 확인 규칙 |

예제·EDA를 직접 실행하려면 완료된 원본을 복사해 자기 ID와 새 번호를 부여한 뒤 실행 안내를 따른다. Git은 `main` 통합, 작업 브랜치 유지, PR 검토 후 일반 병합 방식으로 운영한다. 커밋에는 `exp`·`feat`·`docs`·`fix` 접두어를 사용하며 자세한 내용은 [기여 규칙](CONTRIBUTING.md#커밋-규칙)을 따른다. 초기 프로젝트 파일은 역할별 여섯 커밋으로 등록하고 최초 push를 마쳤다. T04의 정책 정리는 완료했으며 팀원 접근 권한·작업 브랜치 구성·병합 담당자는 별도 운영 준비로 확인한다.

## 접근 방법

| 모델 | 입력·접근 방법 | 비교 목적 |
| --- | --- | --- |
| RGB U-Net | RGB 이미지 | 기본 성능 확인 |
| ELA U-Net | JPEG 재압축 전후 차이인 ELA 이미지 | 압축 오차의 검출 기여 확인 |
| RGB+ELA U-Net | 같은 이미지의 RGB와 ELA 결합 | 두 정보의 결합 효과 확인 |
| CAT-Net | 공식 모델의 입력·전처리와 사전 학습 가중치 | 기존 포렌식 모델과 비교 |

세 U-Net의 기본 비교에서는 입력 채널 수를 제외한 구조, 데이터 분할, 학습 예산, 손실 함수, 평가 조건을 동일하게 맞춘다. 입력 채널 수에 따른 첫 합성곱의 차이는 기록한다. CAT-Net은 고유한 JPEG·DCT 처리와 입력 요건을 따르며, U-Net과의 차이를 보고서에 명시한다. CAT-Net의 가중치·학습 데이터와 평가 데이터의 중복 가능성도 확인한다.

기본 비교를 마친 후 새로운 실험에서 조건을 개선한다. **JPEG 증강은 후순위 작업**이며, 현재 공통 코드에는 증강 기능을 넣지 않는다. ELA 계산에 필요한 JPEG 재압축은 포함한다.

## 프로젝트 구조

```text
ai_forensics/
├── README.md
├── CONTRIBUTING.md
├── AGENTS.md
├── TODO.md
├── .gitignore
├── data/
│   ├── .gitkeep
│   └── README.md
├── models/
│   └── pretrained/
│       ├── README.md
│       └── catnet/
├── notebooks/
│   ├── rgb_unet/
│   ├── ela_unet/
│   ├── rgb_ela_unet/
│   ├── catnet/
│   └── eda/
├── docs/
│   ├── results.md
│   ├── rgb_unet/
│   ├── ela_unet/
│   ├── rgb_ela_unet/
│   ├── catnet/
│   └── eda/
└── scripts/
    ├── __init__.py
    ├── preprocessing.py
    ├── evaluation.py
    ├── datasets.py
    ├── catnet.py
    ├── create_autosplice_split.py
    └── splits/
        ├── README.md
        └── autosplice_seed42.csv
```

빈 폴더의 `.gitkeep`은 폴더 구조를 보존하기 위한 파일이다. 현재 EDA 폴더에는 실행·출력 검토를 마친 평가 함수 사용 예제와 데이터 EDA 노트북, 각각의 보고서가 있다. 새 학습 노트북은 최선 체크포인트를 공유 Drive의 `AI_Forensics/project/models/checkpoints/<모델명>/<실험파일명>_best.pt`에 자동으로 보관한다. 모델별 경로와 확인 절차는 [학습 체크포인트 보관](docs/workflow.md#학습-체크포인트-보관)을 따른다. 예측 이미지·지표 JSON의 저장 위치는 아직 정하지 않았다.

로컬에서 데이터 로드·분석 코드를 작성할 때는 [data/README.md](data/README.md)의 배치 안내를 따른다. `data/`에는 안내와 `.gitkeep`만 추적하고 실제 데이터는 Git에서 제외한다. 기존 001·002의 Colab 실행 구성은 유지하며, 로컬용 노트북은 새 개인 번호로 작성하고 실행 환경을 구분해 기록한다.

## 제안서와 실행 규약

참고 자료는 `10조_Proposal.pdf`(3쪽)와 수업 안내 `ML_team_projects.pdf`(2쪽)이며, 원본 PDF는 저장소에 포함하지 않는다. 아래는 제안서의 계획과 현재 구현을 대조한 내용이다. **제안서의 모든 값을 팀 실행 규약으로 확정한 것은 아니다.** 미정 항목은 T05·T06에서 실제 데이터와 실행 가능성을 확인한 뒤 확정한다.

| 항목 | 제안서에 적힌 계획 | 현재 확인할 사항 |
| --- | --- | --- |
| 데이터 | AutoSplice로 학습, 원본 이미지 기준 80/10/10 분할; CocoGlide는 외부 테스트 | 고정 CSV·파일 연결·Colab 접근·정확한 중복 검사 확인 완료. train–val 중복 1쌍 검토 후 기존 분할 유지 확정(2026-11-24) |
| U-Net | ImageNet 사전학습 ResNet-50 인코더, 6채널 모델의 ELA 입력 가중치는 RGB 가중치 복사 | 구현·초기화 세부 방식과 공통 학습 조건 확정 |
| CAT-Net | `CAT_full_v2`를 AutoSplice JPEG 100으로 파인튜닝; 비교표에는 사전학습·파인튜닝 모두 표기 | 사전학습 모델 검증과 파인튜닝을 구분해 비교 범위 확정 |
| 전처리 | 16의 배수 좌표·크기로 크롭 후 ELA 계산, 같은 좌우반전 적용; 리사이즈·회전 제외 | ELA(quality=90, scale=15, subsampling=2), 원본 ELA 선계산, 256×256 크롭, 평가 시 32의 배수 우하단 제로 패딩·언패딩 확정 |
| 학습 | BCE+Dice, Adam 학습률 1e-4, 검증 성능에 따른 조기 종료 | 손실 비중·배치 크기·학습량·시드·종료 조건 확정 |
| 평가 | 원본 해상도, 임계값 0.5, JPEG 100/90/75; 조작 이미지별 F1·IoU 평균과 정상 픽셀 오탐률 분리 | 현재 함수 초안과 방향은 일치하나 빈 마스크·정상 오탐률 집계·해상도 처리 세부 규약은 미확정 |

제안서에는 파라미터 수, 전처리를 포함한 추론 시간, 조작 영역 크기별 분석도 포함돼 있다. Pixel F1 0.75는 목표이며 측정 결과가 아니다. JPEG 품질 증강은 기본 비교 이후 작업으로 계속 보류한다.

수업 안내 PDF에는 최종 발표가 2026-12-08 예정이며 발표 형식·제출 요건은 추후 공지된다고 적혀 있다. 이후 공지는 별도로 확인해야 한다.

## 필수 실행 환경 — 실험 시작 전 확정

기본 실행은 로컬 노트북을 VS Code에서 열고 Google Colab 확장의 원격 커널로 진행한다. 로컬 실행용 작성은 [data 안내](data/README.md)를 따른다. 실행 출력을 포함해 로컬 `.ipynb`를 저장하고, 그 파일을 기준으로 보고서를 작성한다. 아래 버전은 아직 합의하지 않았으므로, **기본 비교 실험을 시작하기 전에 이 표를 채워야 한다.** 현재 컴퓨터의 Python 버전을 팀 공통 버전으로 간주하지 않는다.

| 항목 | 필수 버전·조건 | 상태 |
| --- | --- | --- |
| Python | 미정 | 실험 시작 전 확정 |
| NumPy | 미정 | 공통 스크립트에 필요 |
| Pillow | 미정 | 이미지 읽기·ELA 생성에 필요 |
| 모델 프레임워크·관련 패키지 | 미정 | U-Net 구현과 CAT-Net 호환성 확인 후 확정 |
| GPU·런타임 | Colab, 세부 조건 미정 | 장치명·메모리·런타임 정보를 실험별 기록 |

버전 확정 후 재현 가능한 설치 명령을 이 문서에 추가한다. 각 노트북의 첫 실행 단계에서 필수 버전 일치 여부를 검사하고, 불일치하면 학습을 시작하지 않는다. GPU 종류처럼 완전히 통일하기 어려운 조건은 반드시 기록한다.

현재 예제·EDA는 NumPy·Pillow·pandas·matplotlib이 필요하며 모델 프레임워크는 사용하지 않는다. 이 단계는 실제 버전과 설정을 출력으로 남겨 실행할 수 있다. 위 버전 일치 검사는 기본 비교 학습을 위한 규칙이며, 현재 노트북에서 팀 필수 버전을 검사하고 있다는 뜻은 아니다.

PyTorch·torchvision 중심의 패키지 구성과 CAT-Net 환경 분리 방안은 [모델 구현 패키지 사용 제안](docs/package_proposal.md)에 정리했다. 팀 검토용 문서이며 패키지 버전·설치 방법을 확정한 것은 아니다.

## CAT-Net 사전학습 모델 평가 — T12

[003 노트북](notebooks/catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.ipynb)과 [보고서](docs/catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.md)에서 CAT_full_v2 가중치 로드와 AutoSplice train 한 장의 입력·추론·시각화·평가를 확인했다(2026-11-20). L4에서 실행했으며 Pixel F1 0.906346, IoU 0.828732는 전체 데이터셋 성능이 아니다.

[004 노트북](notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb)과 [보고서](docs/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md)에서 공통 함수로 AutoSplice test·CocoGlide 2,257장을 평가하고 그림 18개를 확인했다. 임계값은 0.5이며 CocoGlide는 PNG를 JPEG100·4:4:4로 변환했다. CocoGlide의 조작 이미지 평균 F1은 0.363874, IoU는 0.287961, 정상 이미지 평균 픽셀 오탐률은 0.166143이다. 변환의 한계와 누락·과검출 사례는 보고서에 기록했다. 사전학습 데이터 중복 검토와 일부 런타임 코드·분할 해시 확인이 남아 T12는 진행 중이다. 003·004는 보존하고 후속 실행은 새 개인 번호로 진행한다.

## CAT-Net 전이학습·파인튜닝 결과 — T21·T22

2026-11-22에 005·006의 A100 학습·체크포인트 재로드·각 2,257장 평가와 그림 13개씩을 확인함. [005 출력부 전이학습](docs/catnet/EXP_kimjaehak_005_catnet_transfer_learning.md)은 epoch 15가 선택됐으며 JPEG100 F1은 0.927879로 개선됐으나 JPEG75 F1은 0.018991, CocoGlide 정상 픽셀 오탐률은 0.807781로 악화됨. [006 전체 파인튜닝](docs/catnet/EXP_kimjaehak_006_catnet_finetuning.md)은 5 epoch 동안 val 개선이 없어 **학습 전 epoch 0을 최종 평가**함. 실행 완료와 학습 개선 성공을 구분함. 원본 노트북은 보존하고 재실험은 새 번호로 진행함. 체크포인트 Drive 보관·팀원 시각 검토 확인은 남아 있음. [학습·보관 안내](docs/catnet_training.md)를 따름. 이번 학습값은 팀 공통 규약의 확정을 뜻하지 않음.

## 공통 코드의 역할

| 파일 | 현재 제공하는 기능 |
| --- | --- |
| `scripts/preprocessing.py` | RGB 읽기, 지정한 전경값의 이진 마스크 읽기, 이미지·마스크 동일 위치 크롭, ELA 생성, 평가용 우하단 제로 패딩·언패딩 |
| `scripts/evaluation.py` | TP·FP·FN·TN 집계, Pixel F1·IoU·픽셀 오탐률 계산 |
| `scripts/datasets.py` | ZIP 복사·SHA-256 확인·압축 해제 및 재사용, AutoSplice 원본 ID 분할 연결, CocoGlide CSV 기반 이미지·마스크 경로 연결 |
| `scripts/catnet.py` | 003 기준 공식 코드·가중치 준비, 사전학습 CAT-Net 로드·독립 JPEG 입력 구성·단일 JPEG 추론. 004 전체 평가 및 005·006 학습 입력·역전파·재로드 연결 확인. 006은 학습 개선 실패 |
| `scripts/create_autosplice_split.py` | ZIP의 원본 ID에서 분할 CSV 최초 생성. 기존 파일 덮어쓰기 방지 |

모델 정의, 손실 함수, 최적화 설정, 학습·검증 반복문, 체크포인트 선택과 예측 시각화는 노트북에 작성한다. `datasets.py`는 데이터 ZIP을 준비하고 파일 경로를 연결하며 이미지 픽셀은 `preprocessing.py`로 읽는다. 공통 학습용 Dataset·DataLoader는 아직 구현하지 않았다. CAT-Net은 공식 모델·입력 로더를 호출하는 부분을 `catnet.py`에서 재사용하며, Drive 마운트·경로·패키지 설치·평가·시각화는 노트북에 둔다. [사용 안내](docs/catnet.md)를 참고한다.

전처리 함수의 입력·출력, 호출 순서, 제안서와의 대응 및 알려진 한계는 [전처리 함수 사용 안내](docs/preprocessing.md)에 정리했다.

## 사전학습 가중치 준비

사전학습 가중치는 `models/pretrained/<모델명>/`에 둔다. CAT-Net은 `models/pretrained/catnet/CAT_full_v2.pth.tar`를 사용한다. **로컬에 가중치를 추가·변경하면 실행 전에 공유 Drive의 `AI_Forensics/project/models/pretrained/`에도 같은 경로로 업로드해야 한다.** `scripts/`처럼 자동 동기화되지 않으며 Git push도 Drive 업로드를 대신하지 않는다.

실행 시 Drive에서 `/content` 아래로 복사하고 파일 크기·SHA-256·로드 결과를 확인한다. 가중치 파일은 Git에서 제외한다. 자세한 절차는 [사전학습 가중치 안내](models/pretrained/README.md)를 따른다.

## 첫 Colab 예제

[평가 함수 사용 노트북](notebooks/eda/EXP_kimjaehak_001_evaluation_example.ipynb)과 [보고서](docs/eda/EXP_kimjaehak_001_evaluation_example.md)에 AutoSplice·CocoGlide 로드, 분할 연결, 설명용 예측의 F1·IoU·오탐률 계산을 담았다. 2026-11-17에 kimjaehak이 VS Code의 Colab 커널에서 실행·저장한 출력을 검토했다. 코드 셀 8개와 예측 사례 10개, 시각화 3개를 확인해 완료로 기록했다. 확정한 노트북은 보존하고 재실행은 새 개인 번호를 사용한다. 설명용 계산값은 모델 성능이 아니다.

현재 예제는 공유 Drive의 `AI_Forensics/datasets`에서 ZIP을, `AI_Forensics/project/scripts`에서 공통 코드·분할 CSV를 읽는다. `AI_Forensics` 바로가기를 MyDrive 최상위에 추가하고 로컬 `scripts/` 전체를 업로드한다. 노트북과 보고서는 로컬에서 관리한다. 정확한 폴더 구조와 최초 연결 절차는 [실행 안내](docs/workflow.md#2-공유-drive-준비)를 따른다.

ZIP 복사·해시 확인·압축 해제는 `datasets.py`의 `prepare_dataset_zip(source, runtime_zip, destination, expected_hash)`으로 처리한다. `source`는 Drive ZIP, `runtime_zip`은 런타임에 복사할 ZIP, `destination`은 해제 위치이며 함수는 해제 위치를 반환한다. Drive 마운트와 각 경로·기대 해시는 노트북에서 지정한다. ZIP은 `/content`에 복사하고 데이터는 `/content/datasets`에 해제해 읽는다. 예제는 코드·분할·데이터 해시와 실제 패키지 버전을 출력한다. 모델 학습 환경의 팀 표준 버전을 확정하는 작업과는 별개다.

AutoSplice는 [고정 CSV](scripts/splits/autosplice_seed42.csv)를 모든 노트북에서 읽는다. 원본 ID 기준 train 1,818개, val 227개, test 228개이며 같은 원본의 조작본과 JPEG 품질 변형은 같은 split이다. CocoGlide는 외부 테스트용으로 유지한다. [분할 기록](scripts/splits/README.md)에 시드·생성 방식·재현 명령이 있다.

## 데이터 EDA — T05

[002 데이터 EDA 노트북](notebooks/eda/EXP_kimjaehak_002_dataset_eda.ipynb)과 [보고서](docs/eda/EXP_kimjaehak_002_dataset_eda.md)의 Colab 저장 출력 검토를 마쳤다(2026-11-17). 두 데이터셋의 전체 파일·마스크·고정 분할·정확한 중복을 검사하고, AutoSplice train의 크기·조작 영역 분포와 마스크 겹침 그림을 확인한다. 테스트 데이터는 무결성·중복 검사에만 사용한다.

코드 셀 10개가 실행됐고 오류 출력은 0개다. 이미지 14,160개·마스크 2,222개의 읽기·값·대응 크기 오류와 파일·RGB 해시 중복은 0개였다. AutoSplice train 전체에서 256×256 크롭이 가능했다. 기존 해제 파일을 재사용했으며 근접 중복은 검사하지 않았다. 이후 팀원이 표본 마스크 9장과 근접 중복을 검토했고, 2026-11-24에 [기존 분할 유지](scripts/splits/README.md#분할-유지-결정--2026-11-24)를 확정했다. 완료된 002는 보존하고 재실행은 새 번호를 사용한다.

## 공통 코드 수정 후 Drive 업로드 — 필수

**로컬 `scripts/`의 공통 코드를 수정하거나 추가하면, 다음 실행 전에 반드시 공유 Drive의 `AI_Forensics/project/scripts/`에도 반영한다.** 현재 실행 방식에는 로컬 코드와 Drive의 자동 동기화가 없다. Colab은 Drive에 업로드된 파일을 읽는다.

1. 수정한 파일을 로컬에 저장하고 Drive의 같은 상대 경로에 업로드한다. 기존 파일은 교체하며 `scripts/scripts/`처럼 폴더가 중첩되지 않도록 한다. 최초 준비 시에는 `__init__.py`와 `splits/`를 포함한 `scripts/` 전체를 올린다. `__init__.py`는 빈 파일이며 `scripts`를 일반 Python 패키지로 지정한다. 이 파일을 추가한 뒤에도 기존 커널의 패키지 캐시가 남을 수 있으므로 커널을 재시작한다.
2. Drive 업로드 완료 후 Colab에서 파일 경로와 내용을 확인한다. 실행에 필요한 분할 CSV 등 관련 파일도 로컬과 일치해야 한다. 분할 목록을 새로 생성하거나 임의로 바꾸는 절차는 아니다.
3. 이미 공통 모듈을 가져온 커널은 이전 코드를 메모리에 가지고 있을 수 있다. 현재 실행 출력을 먼저 저장하고, 변경한 코드로 실행할 때는 커널을 재시작한 뒤 작성 중인 노트북을 위에서부터 실행한다. 확정한 노트북의 재실행은 새 개인 번호를 사용한다.
4. 실행 시 출력되는 공통 코드의 SHA-256을 확인하고 저장한다. 실행 중에는 공유 공통 코드를 교체하지 않도록 팀원과 업로드 시점을 맞춘다.

노트북은 로컬에서 열고 실행 출력을 포함해 저장한다. 공통 코드를 바꾼 사람은 Drive 반영까지 완료한 뒤 팀원이 실행할 수 있도록 한다.

## 공통 함수 호출 예시

ELA 설정은 공통 함수에 명시적으로 전달한다. 평가 임계값 적용, 정상·조작 이미지 구분, 이미지별 점수 평균은 노트북에서 처리한다. 프로젝트 루트를 작업 경로로 설정하면 다음과 같이 가져올 수 있다.

```python
from scripts.preprocessing import load_rgb, load_binary_mask, make_ela
from scripts.evaluation import confusion_counts, pixel_f1, iou, false_positive_rate

# 경로, mask_foreground, ela_quality, ela_scale, jpeg_subsampling,
# threshold는 실험 설정 셀에서 먼저 정의한다.
rgb = load_rgb(image_path)
mask = load_binary_mask(mask_path, foreground_value=mask_foreground)
ela = make_ela(rgb, quality=ela_quality, scale=ela_scale, subsampling=jpeg_subsampling)
# probabilities는 모델의 sigmoid 등으로 얻은 (H, W) 확률 배열이다.
prediction = probabilities >= threshold
tp, fp, fn, tn = confusion_counts(mask, prediction)

f1 = iou_score = fpr = None
if tp + fn > 0:
    f1 = pixel_f1(tp, fp, fn)
    iou_score = iou(tp, fp, fn)
else:
    fpr = false_positive_rate(fp, tn)
```

ELA는 `clip(round(scale * abs(RGB - JPEG(RGB))), 0, 255)`로 계산한 RGB 순서의 `uint8` 배열이다. 품질, 증폭률, 서브샘플링을 기록한다. 이미지별 최댓값으로 다시 정규화하지 않는다. 기본 비교에서는 원본에서 ELA를 먼저 계산한 뒤 크롭하며, 평가 시에는 32의 배수로 우하단 제로 패딩하고 추론 후 원본 크기로 언패딩한다. CAT-Net의 입력은 이 함수로 임의 대체하지 않는다.

`confusion_counts`는 같은 크기의 비어 있지 않은 2차원 이진 마스크를 받고 `(tp, fp, fn, tn)`을 반환한다. 세 지표 함수에는 여기서 구한 개수를 전달하며, 각 식의 분모가 0이면 `None`을 반환한다. 확률 변환·검사와 임계값 적용은 노트북에서 수행한다.

지표 함수 자체는 정상·조작 이미지를 구분하지 않는다. 정상 이미지에 오탐이 있으면 `pixel_f1`·`iou`를 직접 호출한 값은 0이므로, 정상 이미지 제외 여부를 `None`만으로 판단하면 안 된다. 위 예시처럼 정답 조작 픽셀 수(`tp + fn`)로 나눠 **조작 이미지에는 F1·IoU, 정상 이미지에는 오탐률**을 계산한다. 이때 이미지 전체의 정답·예측을 사용한다.

이미지별 결과를 모으고 데이터셋·분할·JPEG 품질별로 평균하는 작업은 노트북에 둔다. 조작 이미지의 F1·IoU 평균과 정상 이미지의 오탐률 평균을 분리하는 집계안의 세부 규약은 T06에서 확정한다. 임계값, 평가 해상도·후처리, 분할과 누수 방지 기준도 함께 확정한다. 테스트 결과로 임계값이나 학습 조건을 선택하지 않는다.

## 실행·기록 순서

1. [기여 규칙](CONTRIBUTING.md)과 [할 일](TODO.md)을 확인한다.
2. 예제·EDA는 해당 작업의 환경·데이터·설정을 확인한다. 기본 비교 학습은 공통 환경·분할·평가 규약을 먼저 확정한다.
3. 담당 작업 브랜치에서 새 번호의 노트북을 만든다. 아직 Git 운영을 시작하지 않았다면 브랜치 작업은 보류한다.
4. VS Code에서 로컬 노트북을 열고 Colab 커널을 선택한다. 원격에 동일한 공통 코드·분할 파일을 준비하고 모듈을 가져올 수 있는지 확인한다.
5. 버전·설정·데이터·코드 버전을 기록하고 위에서 아래로 실행한다. 최종 검증은 작성 중인 노트북의 커널을 재시작하고 이전 출력을 지운 상태에서 진행한다.
6. 실행 출력이 포함된 로컬 `.ipynb`를 저장하고 다시 열어 확인한다. 실패·중단 시에도 오류와 실행 상태를 보존한다.
7. 저장된 출력을 기준으로 같은 이름의 보고서와 [통합 점수표](docs/results.md)를 직접 갱신한다.
8. 숫자와 링크를 확인하고 TODO를 갱신한 뒤 실험을 확정한다.

실험 파일명은 `EXP_Git이름_개인실험번호_실험내용`을 사용한다. 예: `EXP_kimjaehak_001_rgb_unet_baseline.ipynb`. 자세한 번호·보존·보고 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)를 따른다.
