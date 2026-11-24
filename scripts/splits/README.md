# AutoSplice 공통 분할

`autosplice_seed42.csv`는 `original_id,split` 두 열로 구성함. 모든 노트북에서 이 파일을 읽으며 실행할 때 다시 분할하지 않음.

| 항목 | 내용 |
| --- | --- |
| 생성일 | 2026-11-17 |
| 대상 | AutoSplice.zip의 Authentic/*.jpg 원본 ID 전체 |
| ID 수 | 2,273 |
| 학습 / 검증 / 테스트 | 1,818 / 227 / 228 |
| 생성 방식 | 숫자순 ID 정렬 → Python random.Random(42).shuffle → 80/10/10 배정 |
| 정수 배정 | 학습 N×80//100, 검증 N×10//100, 나머지 테스트 |
| CSV 정렬 | original_id 숫자순 |
| 생성 환경 | Python 3.9.6, Python 3.12.14에서 동일 파일 재현 확인 |

같은 원본의 정상 이미지·조작본·JPEG 100/90/75 변형은 같은 split에 포함함. 조작본이 없는 정상 원본도 포함함. 원본당 조작본 수가 달라 파일 수의 비율은 정확히 80/10/10이 아닐 수 있음. [002 EDA](../../docs/eda/EXP_kimjaehak_002_dataset_eda.md)에서 파일·RGB 해시 기준의 정확한 중복은 발견되지 않음. 근접 중복에 대한 팀 결정은 아래에 기록함.

성능을 보고 시드를 선택하지 않음. 시드 42는 이번 최초 생성에 사용한 값이며, 이후에는 저장된 CSV가 기준임. 분할을 바꾸는 실험은 다른 파일명과 새 실험 번호로 기록함. CocoGlide는 분할하지 않고 전체를 외부 테스트용으로 유지함.

## 분할 유지 결정 — 2026-11-24

팀은 확인된 분할 간 중복의 범위가 작다고 판단해 11월 23일의 새 분할 생성 계획을 철회하고, 기존 `autosplice_seed42.csv`를 기본 비교에 계속 사용하기로 합의함. 분할 간에 확인된 같은 사진은 AutoSplice `46217`(train)과 `54313`(val) 한 쌍임. 두 ID와 파생 파일은 기존 분할에 두고 train 내부에서 확인된 9쌍도 유지함. [근접 중복 검토 결과](../../docs/eda/EXP_seonghun_002_near_duplicate_feature_check.md)

검증 원본 ID 227개 중 1개(약 0.44%)가 학습 원본과 겹침. 검증 점수·조기 종료·체크포인트 선택을 해석할 때 이 한계를 기록함. 실제 점수에 미치는 영향은 미측정임. 이번 검사에서 AutoSplice test 또는 CocoGlide와의 교차 중복은 발견되지 않았음.

## 파일 확인

| 파일 | SHA-256 |
| --- | --- |
| AutoSplice.zip | `0d94e2df6842f44c11e21ee207707c49fd9717ec89048bd6f28fc1e07c4a5e36` |
| autosplice_seed42.csv | `f8a2893ab93b82264e6434fa0c26f09472de05bd98829065c2a0db846ace7b1e` |

## 재현

프로젝트 루트에서 실행함. 생성기는 기존 파일을 덮어쓰지 않음. 아래 명령은 원본 CSV를 건드리지 않고 별도 파일을 생성함.

```bash
python scripts/create_autosplice_split.py /path/to/AutoSplice.zip /tmp/autosplice_seed42_check.csv --seed 42
```

[사용 예제](../../notebooks/eda/EXP_kimjaehak_001_evaluation_example.ipynb) · [보고서](../../docs/eda/EXP_kimjaehak_001_evaluation_example.md)
