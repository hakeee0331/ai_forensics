# CAT-Net 전체 파인튜닝 시도

| 항목 | 내용 |
| --- | --- |
| 작성자·실행자 | kimjaehak |
| 실행일·출력 검토일 | 2026-11-22 |
| 상태 | 실행·저장 출력 검토 완료. 학습 개선 실패·epoch 0 선택. 체크포인트 외부 보관·팀원 시각 검토 확인 대기 |
| 노트북 | [EXP_kimjaehak_006_catnet_finetuning.ipynb](../../notebooks/catnet/EXP_kimjaehak_006_catnet_finetuning.ipynb) |
| 실행·보관 안내 | [CAT-Net 학습 절차](../catnet_training.md) |
| 기준 결과 | [004 사전학습 평가](EXP_kimjaehak_004_catnet_pretrained_evaluation.md) |
| 관련 작업 | T22. 실행 완료와 팀 규약 확정을 구분함 |

## 목적·가설

동일한 CAT_full_v2에서 시작해 학습 범위가 내부 검증·테스트와 외부 일반화에 미치는 영향을 확인함. 005는 last_layer만, 006은 전체 파라미터를 학습함. 006은 005 결과에서 이어 학습하지 않음. 정상 픽셀 오탐률을 조작 F1·IoU와 함께 평가함.

## 실제 모델·데이터·학습 설정

| 항목 | 실제 조건 |
| --- | --- |
| 학습 범위 | `full` — 전체 파라미터 학습. BatchNorm affine 파라미터 포함 |
| 초기 가중치 | CAT_full_v2. 005·006 모두 원래 사전학습 모델에서 독립적으로 시작 |
| 출력부 | 사전학습 last_layer 유지. 재초기화·클래스 변경 없음 |
| BatchNorm | running mean/variance는 두 실험 모두 고정. affine 파라미터는 해당 학습 범위에 따름 |
| train | AutoSplice 고정 CSV train, JPEG100 조작본+정상 원본. 각 파일을 epoch당 한 번 사용 |
| val | AutoSplice 고정 CSV val 전체, 원본 해상도 |
| 학습 입력 | 공식 JPEG RGB+DCT+qtable 구성 후 원본 안에서 256×256 크롭. 좌표는 16의 배수 |
| 증강 | 크롭 외 없음. 좌우반전·회전·리사이즈·JPEG 증강 없음 |
| 손실 | BCEWithLogits(logit1-logit0)+soft Dice, 1:1, smooth=1. 정상·빈 크롭도 포함 |
| optimizer | Adam, lr=1e-4, weight_decay=0, 기본 betas·eps, 스케줄러 없음 |
| 학습량 | 배치 2, FP32, 최대 20 epoch, val loss patience 5 |
| 시드 | 42. 크롭은 seed·epoch·index, shuffle은 seed+epoch |
| 선택 | 전체 val 이미지별 평균 손실 최소. epoch 0도 후보, 동률은 먼저 나온 epoch |
| 예비 점검 | train 정상·조작 각 한 장의 3 step. 검사 후 초기 가중치 복원·optimizer 폐기 |
| 체크포인트 | `/content/checkpoints/EXP_kimjaehak_006_catnet_finetuning_best.pt`, 런타임 저장·재로드 확인, Drive 보관 확인 대기 |

위 값은 이번 실행의 실제 설정이며 팀 공통 학습 규약의 최종 승인을 뜻하지 않음. 두 노트북의 공통 설정 서명과 실행 환경이 일치함.


train은 조작 2,925장·정상 1,818장, val은 조작 361장·정상 227장임. 원본 ID는 train/val/test 1,818/227/228개이며 분할 중복 검사를 통과함. 전체 파라미터 114,263,810개 중 114,263,810개 모두 학습 대상으로 설정함.

## 학습·선택 결과

**5 epoch 학습 후 개선이 없어 epoch 0을 선택함. 아래 테스트 점수와 그림은 파인튜닝된 가중치의 결과가 아니라 학습 전 사전학습 가중치를 재로드한 결과임.** 실행 오류 없이 절차는 끝났지만 학습 개선에는 실패함.

epoch 1의 평균 train loss가 22,663.437917로 급증했고 epoch 1~5의 val F1·IoU·정상 FPR은 모두 0임. 조작 정답 픽셀을 검출하지 못하는 상태이며 정상 쪽으로 치우친 양상임. 집계값만으로 조작 이미지의 모든 예측 픽셀이 0이라고 단정하지 않음. 학습 후 epoch 1~5의 test 성능은 측정하지 않음.

| epoch | train loss | val loss | val F1 | val IoU | 정상 val FPR |
| --- | --- | --- | --- | --- | --- |
| 0 (선택) | 해당 없음 | 0.780755 | 0.851659 | 0.774502 | 0.118912 |
| 1 | 22663.437917 | 1.376014 | 0.000000 | 0.000000 | 0.000000 |
| 2 | 1.387113 | 1.377605 | 0.000000 | 0.000000 | 0.000000 |
| 3 | 1.386731 | 1.378916 | 0.000000 | 0.000000 | 0.000000 |
| 4 | 1.386575 | 1.380026 | 0.000000 | 0.000000 | 0.000000 |
| 5 | 1.386418 | 1.380713 | 0.000000 | 0.000000 | 0.000000 |

작은 배치 3-step loss는 0.611584 → 1.988678 → 1.200714임. 1,465개 파라미터 텐서 갱신과 고정값·BN 통계 보존 검사를 통과하고 초기 가중치를 복원한 뒤 본 학습을 시작함. 이는 역전파 동작 확인이며 전체 학습의 안정성 보장이 아님.

학습·검증·체크포인트 저장 포함 시간은 6561.419초, 해당 구간 최대 GPU 할당은 5.838236GiB임. 전체 VRAM 사용량이나 추론 시간 측정값이 아님.

## 테스트 평가

총 2,257장 평가를 확인함. 임계값 0.5, 원본 해상도, 조작 이미지별 F1·IoU와 정상 이미지별 픽셀 오탐률을 각각 평균함. CocoGlide 1,024장은 PNG→RGB JPEG100·4:4:4로 변환함. 정상 AutoSplice는 품질별 중복 집계하지 않음. 테스트로 체크포인트·임계값을 선택하지 않음.

| 데이터·조건 | 조작/정상 수 | Pixel F1 | IoU | 정상 픽셀 오탐률 |
| --- | --- | --- | --- | --- |
| AutoSplice JPEG100 | 335 / 0 | 0.881534 | 0.804299 | 해당 없음 |
| AutoSplice JPEG90 | 335 / 0 | 0.804909 | 0.717195 | 해당 없음 |
| AutoSplice JPEG75 | 335 / 0 | 0.402966 | 0.320134 | 해당 없음 |
| AutoSplice original | 0 / 228 | 해당 없음 | 해당 없음 | 0.146547 |
| CocoGlide PNG→JPEG100·4:4:4 | 512 / 0 | 0.363896 | 0.287980 | 해당 없음 |
| CocoGlide PNG→JPEG100·4:4:4 | 0 / 512 | 해당 없음 | 해당 없음 | 0.166196 |

노트북에 저장된 이미지별 TP·FP·FN·TN 2,257행에서 지표를 재계산해 표시된 6집단 평균과 일치함을 확인함. 두 실험의 이미지 목록·크기·정답 양성 수가 일치함. 정상 이미지의 F1·IoU 및 조작 집단의 정상 FPR은 해당 없음임.

## 정성 검토·해석 — 2026-11-22, Codex

학습 크롭 1개와 테스트 그림 12개를 확인함. 크롭의 마스크 오버레이는 표시된 영역과 겹침. 이는 저장 그림의 검토이며 데이터셋 전체 정답의 적절성에 대한 팀원 승인이 아님. 테스트 그림은 6집단에서 seed 42로 각 2장을 선택했으며 최초 평가의 혼동행렬과 일치 검사를 통과함.

아래 그림은 모두 epoch 0 모델임. 학습이 붕괴한 epoch 1~5의 예측 그림이 아님.

- JPEG100 `41619_2.jpg`·`48344_1.jpg`: 조작 영역을 대체로 검출함(F1=0.9753·0.9225).
- JPEG75 `43680_0.jpg`는 표지판을 부분 검출함(F1=0.7712). `40740_0.jpg`는 음식 주변 배경까지 과검출함(F1=0.5804).
- JPEG90 `54827_1.jpg`·`60785_1.jpg`: 인물 영역을 대체로 검출함(F1=0.9624·0.9468).
- 정상 AutoSplice `53693.jpg`는 넓은 오탐(FPR=0.6603), `47509.jpg`는 오탐 없음임.
- CocoGlide `glide_inpainting_val2017_532129_up.png`·`glide_inpainting_val2017_78959_up.png`: 조작 영역을 대부분 놓침(F1=0.0940·0.0464). 정상 `toothbrush_365385.png`·`laptop_11813.png`에도 국소 오탐이 있음(FPR=0.0237·0.0403).
- 전체 CocoGlide 조작 512장 중 117장은 예측 양성이 없고 155장은 TP=0임. 정상 512장 중 201장은 오탐 픽셀이 없음.

004와 거의 같은 사전학습 성능을 확인함. 소수점 이하 차이는 기록 그대로 보존함. 004와 GPU·수치 연산 설정 등이 다르므로 비트 단위 동일성을 주장하지 않으며, 이 작은 차이를 파인튜닝 효과로 해석하지 않음.

첫 epoch의 큰 손실은 최적화 불안정성을 우선 점검할 근거임. 현재 코드는 전체 모델에 Adam 1e-4를 적용하고 gradient norm의 유한성만 확인함(`max_norm=inf`). 유한하지만 큰 gradient를 제한하는 clipping은 수행하지 않음. 학습률·층별 갱신 범위·BN 고정·손실 구성의 영향은 가설이며 배치별 loss·gradient·logit 기록이 없어 원인을 확정할 수 없음.

## 실행 환경·코드 버전

| 항목 | 저장 출력 |
| --- | --- |
| Python / CUDA | 3.13.16 / 13.0 |
| GPU | NVIDIA A100-SXM4-80GB, 장치 메모리 79.25GiB |
| torch / torchvision | 2.14.1+cu130 / 0.29.1+cu130 |
| NumPy / Pillow / JPEG | 2.4.6 / 11.3.0 / 6.2 |
| pandas / matplotlib | 2.2.3 / 3.10.0 |
| pyjpegio / yacs / PyYAML | 0.3.0 / 0.1.8 / 6.0.3 |
| torch-dct / opencv-python / tqdm | 0.1.6 / 5.0.0.93 / 4.67.3 |
| 재현 설정 | seed 42, TF32 비활성, cuDNN deterministic, deterministic algorithms warn_only |
| 공통 설정 서명 | `de71b209c1025273c035762134f7120857e875a2892d7bcbf7fa8318b09b0113` |

공통 코드 기준 커밋은 `17fa55027c3d331979abf14a2039ad21e017dfb7`임. 노트북은 이후 추가된 파일이며 이 커밋에 포함됐다고 기록하지 않음. Drive의 실제 모듈 경로와 다음 해시 일치를 출력에서 확인함.

| 파일 | 런타임 SHA-256 |
| --- | --- |
| `scripts/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `scripts/catnet.py` | `04d2d6561caf27ae83ccff844adf2b71c02d48470a37359d268f2ee8e217c889` |
| `scripts/datasets.py` | `435215ef08c2c43ce2f84795d783895074eee85f8e062f28ea8ee6acabad3e88` |
| `scripts/preprocessing.py` | `73ce7fa0aee3f2b901a9ab04d430ff8ae2bcaa7262005600f6b08f04b95c652f` |
| `scripts/evaluation.py` | `ad400aa2cf453bd54ecc3e73abc38bc80cb1f7239eea7489b3072dae96dfcb52` |
| `scripts/splits/autosplice_seed42.csv` | `f8a2893ab93b82264e6434fa0c26f09472de05bd98829065c2a0db846ace7b1e` |


공식 코드 커밋: `5eb85900b0e72423c95a8d41bc835b86c8671f8a`. 초기 가중치 SHA-256: `f82aaafdd1142775231feedcea0bb7027f7370561d9e8d107465454001865989`(915,503,873바이트, 공식 epoch 196). 이 공식 epoch와 본 실험의 epoch 번호는 서로 다름.

검토한 노트북 SHA-256: `9d577a577ec65e0f747ac11ea3693d53b5769947b25139f1f930139e00b5dc42`.

## 체크포인트·보관 상태

- 파일명: `EXP_kimjaehak_006_catnet_finetuning_best.pt`.
- 런타임 저장 위치: `/content/checkpoints/EXP_kimjaehak_006_catnet_finetuning_best.pt`.
- Drive 보관 경로: `AI_Forensics/project/models/checkpoints/catnet/EXP_kimjaehak_006_catnet_finetuning_best.pt`. [복사·해시 확인 절차](../catnet_training.md#체크포인트-보관재시작)를 따름. 실제 Drive 복사 완료는 아직 미확인임.
- SHA-256: `b378861f61ee856e638c3ead2313c38b9d1aceaf2e3f7a3227b9623b97e14365`.
- 선택 epoch: 0. **학습 전 초기 가중치임. 파인튜닝 개선 모델로 표시하지 않음**.
- 저장 전후 val 표본 예측의 최대 절대 오차 0.0으로 재로드 검사를 통과함.
- `state_dict`, 환경·설정·코드 해시, 선택 epoch·val 지표, 선택 시점까지의 history와 재로드 대조용 예측을 포함함. 학습 epoch 1~5 이력은 best 파일에 포함되지 않으므로 전체 이력은 노트북 출력으로 보관함.
- optimizer·난수 상태는 없어 정확한 이어 학습용 체크포인트가 아님. `from_pretrained`는 공식 가중치 해시를 검사하므로 이 파일을 직접 전달하지 않음.
- 다운로드 셀 실행은 확인했지만 실제 파일 다운로드·Drive 보관은 별도 확인이 필요함. `.ipynb` 저장은 가중치 보관을 대신하지 않음.

## 검증 범위·후속 작업

코드 셀 15개, 실행번호 4~18, 오류 출력 0개, PNG 13개를 확인함. 실행번호만으로 깨끗한 커널에서 시작했다고 단정하지 않음. 공식 코드의 `F.upsample` 폐기 예정 경고와 배열 목록의 텐서 변환 성능 경고가 있으나 예외는 발생하지 않음. 이 경고가 성능 저하의 원인이라고 단정하지 않음.

노트북 첫 상태와 마지막 사람 검토 메모에는 준비 시 문구가 남아 있음. 저장된 원본을 수정하지 않고 실제 실행 상태는 이 보고서와 TODO에 기록함. 팀원의 마스크·예측 검토 확인은 아직 없음. 사전학습 데이터 중복 가능성, 정상·조작 JPEG 이력 차이, PNG 변환의 한계와 T03·T05·T06·T19의 최종 합의는 남아 있음.

후속 실험에서는 train·val의 배치별 손실·logit·gradient norm부터 확인하고, 학습률·갱신 범위를 통제해 안정성을 점검해야 함. 현재 결과는 CAT-Net 파인튜닝 자체가 불가능하다는 증거가 아님. 테스트 결과를 보고 임계값·학습률을 고르지 않으며 재실험은 새 개인 번호를 사용함. 공통 스크립트와 실행된 005·006은 변경하지 않음.
