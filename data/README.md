# 로컬 데이터 준비

로컬에서 데이터 로드·분석 코드를 작성할 때 사용하는 폴더임. 데이터는 각자 준비하며, Git에는 이 안내와 `.gitkeep`만 포함함. ZIP·이미지·마스크·데이터셋 메타데이터는 업로드하지 않음.

## 권장 배치

공유 Drive의 `AI_Forensics/datasets/AutoSplice/AutoSplice.zip`과 `AI_Forensics/datasets/CocoGlide.zip`을 받아 아래처럼 배치함. 아래 데이터 폴더와 파일은 예시이며 저장소에서 제공하지 않음.

```text
data/
├── .gitkeep
├── README.md
├── archives/
│   ├── AutoSplice.zip
│   └── CocoGlide.zip
├── AutoSplice/
│   ├── Authentic/
│   ├── Caption/
│   ├── Forged_JPEG100/
│   ├── Forged_JPEG90/
│   ├── Forged_JPEG75/
│   └── Mask/
└── CocoGlide/
    ├── real/
    ├── fake/
    ├── mask/
    ├── table.csv
    ├── README.txt
    └── licenses.json
```

AutoSplice ZIP은 내부에 `AutoSplice/`가 있으므로 `data/`에 해제함. CocoGlide ZIP은 `real/`, `fake/`, `mask/` 등이 바로 들어 있으므로 `data/CocoGlide/`에 해제함. `data/AutoSplice/AutoSplice/`처럼 중첩되지 않도록 확인함. ZIP에 포함된 다른 설명·메타데이터 파일도 그대로 보관함.

## 공통 코드와 연결

로컬 코드의 프로젝트 루트를 기준으로 다음 경로를 사용함. 노트북을 연 위치에 따라 현재 작업 폴더가 달라질 수 있으므로 루트에 `scripts/`가 있는지 먼저 확인함.

| 용도 | 프로젝트 루트 기준 경로 |
| --- | --- |
| AutoSplice 로더의 root | `data/AutoSplice` |
| CocoGlide 로더의 root | `data/CocoGlide` |
| AutoSplice 고정 분할 | `scripts/splits/autosplice_seed42.csv` |

`scripts.datasets`의 `autosplice_records`, `cocoglide_records`에는 위 데이터 경로를 전달함. 이미지·마스크는 [공통 전처리 함수](../docs/preprocessing.md)로 읽음. 원본 ID 분할 CSV는 저장소의 파일을 그대로 읽고 로컬에서 다시 생성하지 않음.

공유 데이터와 같은 ZIP인지 아래 SHA-256으로 확인할 수 있음. 계산에는 `scripts.datasets.sha256`을 사용할 수 있음. 해시가 다르면 원본 파일을 확인하고, 기대값을 임의로 바꾸지 않음.

| ZIP | SHA-256 |
| --- | --- |
| AutoSplice.zip | `0d94e2df6842f44c11e21ee207707c49fd9717ec89048bd6f28fc1e07c4a5e36` |
| CocoGlide.zip | `fc848643ad0a81010ba2a6ab8c055762782f54e4fb9e407210dbfe1c3b538af9` |

## 노트북·실험 기록

현재 001·002는 Drive를 마운트하는 Colab용 노트북이며 로컬에서 그대로 실행하는 구성이 아님. 로컬용으로 작성할 때는 새 개인 번호로 복사하고, 복사본에서 Drive 마운트와 `/content` 경로를 로컬 경로로 바꿔야 함. 완료된 원본과 저장 출력은 보존함.

로컬 실행도 [기여 규칙](../CONTRIBUTING.md)의 파일명·출력 저장·보고서 작성 절차를 따름. 실제 Python·패키지 버전·OS·장치·공통 코드 버전과 설정을 기록하고 실행 환경을 `로컬`로 명시함. Colab 결과나 팀원 검증 완료로 기록하지 않음. 기본 비교 학습의 공통 환경·학습·평가 조건은 별도로 맞춰야 함.

이 폴더는 데이터 배치 안내이며 로컬용 노트북·설치 환경을 제공하거나 실행 검증을 완료했다는 의미는 아님. Colab 실행은 기존 [실행 안내](../docs/workflow.md)를 따름.
