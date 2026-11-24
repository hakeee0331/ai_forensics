# 실험 결과

- CAT-Net v2의 단일 이미지 확인과 AutoSplice test·CocoGlide 전체 2,257장 평가, 저장된 그림 18개 검토를 마쳤다(2026-11-20).
- 여러 모델 간 비교·학습·파인튜닝은 아직 실행하지 않았다. 평가 함수 사용 예제, 데이터 EDA, 전처리 실데이터 검증은 Colab 실행·저장 출력 검토를 완료했다(2026-11-17~18).
- RGB·ELA·RGB+ELA U-Net 기본 비교(kimjihwan 002~004)를 같은 조건으로 학습·평가했다(2026-11-24, L4). 파인튜닝한 CAT-Net과의 비교는 아직 없다.
- T05의 분할 최종 확정과 T06의 공통 규약 확정, 팀원 검증은 남아 있다. 설명용 예측의 계산값은 모델 점수표에 넣지 않는다.

## 평가 조건

AutoSplice는 [고정 분할 CSV](../scripts/splits/autosplice_seed42.csv)를 사용하고 CocoGlide는 외부 테스트용으로 유지한다. 공통 평가 규약 전체는 아직 미정이며, 임계값·해상도·후처리·집계의 세부 조건은 T06에서 확정한다. 공통 함수는 TP·FP·FN·TN과 개별 지표만 계산하고, 분모가 0이면 해당 지표는 `None`을 반환한다. 정상·조작 이미지 구분과 이미지별 평균은 노트북에서 처리한다. 조작 이미지의 F1·IoU와 정상 이미지의 픽셀 오탐률을 분리해 평균하는 안을 검토 중이다.

점수는 0~1 범위로 기록하고 표시 자릿수를 맞춘다. 정상 이미지가 없는 평가에서는 오탐률을 `미측정`으로 표시한다. 평가 조건이 다른 결과는 별도 표로 분리한다. 조건에는 데이터셋·분할 식별자, 해상도·임계값·후처리, 원본 또는 명시된 JPEG 품질 등을 포함한다. ELA 재압축 품질은 입력의 JPEG 평가 품질과 별개로 기록한다.

## 모델 실험

004는 임계값 0.5·원본 해상도에서 이미지별 점수를 평균함. 정상 원본은 품질별로 중복 집계하지 않음. CocoGlide 입력은 PNG→JPEG100·4:4:4이며 원본 PNG를 그대로 사용한 평가가 아님. 아래 오탐률은 정상 이미지별 **픽셀 오탐률의 평균**임. 사전학습 데이터 중복 검토와 일부 런타임 해시 확인은 남아 있으며, 상세한 입력 조건·그림·재현 한계는 [004 보고서](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md)에 기록함. T12는 진행 중임.

kimjihwan 002~004는 AutoSplice train 조작 이미지(JPEG100, 정상 제외)로 학습한 ResNet-50 U-Net이며, 손실 `bce_dice`, 시드 42, L4에서 실행함. 평가는 004와 같은 조건(임계값 0.5, 원본 해상도, `pad_image`·`unpad_image`, 이미지별 평균)임. 002는 손실 세 조건 중 val로 선택된 `bce_dice`만 표에 넣었고 나머지는 보고서에 있음. U-Net은 AutoSplice로 학습했고 CAT-Net 004는 사전학습 모델이라 학습 조건이 다름.

| 실험·보고서 | 모델 | 데이터셋·분할 | 평가 조건 | 조작/정상 수 | Pixel F1 | IoU | 정상 픽셀 오탐률 | 상태 | 노트북 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | AutoSplice test | JPEG100, 임계값 0.5 | 335 / 0 | 0.881532 | 0.804299 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | AutoSplice test | JPEG90, 임계값 0.5 | 335 / 0 | 0.804874 | 0.717161 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | AutoSplice test | JPEG75, 임계값 0.5 | 335 / 0 | 0.402828 | 0.320014 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | AutoSplice test | 정상 JPEG 원본, 임계값 0.5 | 0 / 228 | 해당 없음 | 해당 없음 | 0.146428 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 512 / 0 | 0.363874 | 0.287961 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [004](catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md) | CAT-Net v2 사전학습 | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 0 / 512 | 해당 없음 | 해당 없음 | 0.166143 | 완료: 저장 출력 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | AutoSplice test | JPEG100, 임계값 0.5 | 335 / 0 | 0.968899 | 0.941057 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | AutoSplice test | JPEG90, 임계값 0.5 | 335 / 0 | 0.278731 | 0.186072 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | AutoSplice test | JPEG75, 임계값 0.5 | 335 / 0 | 0.005337 | 0.002859 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | AutoSplice test | 정상 JPEG 원본, 임계값 0.5 | 0 / 228 | 해당 없음 | 해당 없음 | 0.000570 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 512 / 0 | 0.360052 | 0.257634 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 002](rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md) | RGB U-Net (bce_dice) | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 0 / 512 | 해당 없음 | 해당 없음 | 0.970198 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | AutoSplice test | JPEG100, 임계값 0.5 | 335 / 0 | 0.957054 | 0.921905 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | AutoSplice test | JPEG90, 임계값 0.5 | 335 / 0 | 0.000959 | 0.000514 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | AutoSplice test | JPEG75, 임계값 0.5 | 335 / 0 | 0.008440 | 0.004907 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | AutoSplice test | 정상 JPEG 원본, 임계값 0.5 | 0 / 228 | 해당 없음 | 해당 없음 | 0.012541 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 512 / 0 | 0.359235 | 0.254559 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 003](ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md) | ELA U-Net | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 0 / 512 | 해당 없음 | 해당 없음 | 0.941426 | 완료: 저장 출력 확인 | [노트북](../notebooks/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | AutoSplice test | JPEG100, 임계값 0.5 | 335 / 0 | 0.971787 | 0.946339 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | AutoSplice test | JPEG90, 임계값 0.5 | 335 / 0 | 0.004701 | 0.002771 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | AutoSplice test | JPEG75, 임계값 0.5 | 335 / 0 | 0.007563 | 0.004829 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | AutoSplice test | 정상 JPEG 원본, 임계값 0.5 | 0 / 228 | 해당 없음 | 해당 없음 | 0.000934 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 512 / 0 | 0.361080 | 0.258603 | 해당 없음 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |
| [kimjihwan 004](rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md) | RGB+ELA U-Net | CocoGlide external_test | PNG→JPEG100, 4:4:4, 임계값 0.5 | 0 / 512 | 해당 없음 | 해당 없음 | 0.975726 | 완료: 저장 출력 확인 | [노트북](../notebooks/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.ipynb) |

실험·보고서 열에는 개별 보고서 링크를, 노트북 열에는 대응하는 노트북 링크를 넣는다. 미실행·실패·미측정 항목을 0으로 기록하지 않는다. 노트북 출력·보고서·이 표의 숫자는 일치해야 한다.

## EDA

| 분석·보고서 | 데이터셋 | 주요 확인 내용 | 상태 | 노트북 |
| --- | --- | --- | --- | --- |
| [EXP_kimjaehak_001_evaluation_example](eda/EXP_kimjaehak_001_evaluation_example.md) | AutoSplice, CocoGlide | 공통 ZIP 준비 함수·고정 ID 분할·파일 연결·이미지 및 마스크 표시·평가 함수 사용법 | 완료: Colab 저장 출력 확인 (2026-11-17) | [노트북](../notebooks/eda/EXP_kimjaehak_001_evaluation_example.ipynb) |
| [EXP_kimjaehak_002_dataset_eda](eda/EXP_kimjaehak_002_dataset_eda.md) | AutoSplice, CocoGlide | 전체 파일·마스크·분할·정확한 중복 검사, AutoSplice train 분포·마스크 시각화 | 완료: Colab 저장 출력 확인, T05 최종 확정 대기 (2026-11-17) | [노트북](../notebooks/eda/EXP_kimjaehak_002_dataset_eda.ipynb) |
| [EXP_byhyun_001_preprocessing_check](eda/EXP_byhyun_001_preprocessing_check.md) | AutoSplice | 이미지·마스크·정상 원본 크기·EXIF 정합성, Crop·뒤집기와 ELA 순서, ELA 수치 처리, 정상·조작 파일의 JPEG 저장 이력, ELA 설정 후보 비교, Crop 크기, 평가 규칙 확인 | 완료: Colab 저장 출력 확인, T06 규약 확정 대기 (2026-11-18) | [노트북](../notebooks/eda/EXP_byhyun_001_preprocessing_check.ipynb) |
| [EXP_kimjihwan_001_unet_pipeline_check](rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.md) | AutoSplice | ResNet-50 U-Net(RGB·ELA·RGB+ELA)의 사전학습 가중치 로드, 3·6채널 입출력 크기, 작은 배치 학습, 체크포인트 재로드, 원본 해상도 추론·평가 함수 연결 동작 확인. 학습 설정은 임시값, 성능 미측정 | 완료: Colab 저장 출력 확인, T03·T06 확정 대기 (2026-11-20) | [노트북](../notebooks/rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.ipynb) |
EDA에는 모델 성능 점수를 만들지 않고 분석 보고서와 노트북을 연결한다.
| [EXP_byhyun_002_preprocessing_padding_check](eda/EXP_byhyun_002_preprocessing_padding_check.md) | AutoSplice | 수정된 입력 검사(`foreground_value`·`scale`)와 평가용 패딩·언패딩 함수 확인(합성 입력, val 조작 이미지 361장) | 완료: Colab 저장 출력 확인 (2026-11-20) | [노트북](../notebooks/eda/EXP_byhyun_002_preprocessing_padding_check.ipynb) |

- 2026-11-17: 002 코드 셀 10개·오류 출력 0개·그림 3개를 확인함. 이미지 14,160개·마스크 2,222개의 읽기·값·대응 크기 오류와 파일·RGB 해시 중복이 0개임. 기존 해제 파일을 재사용했으며 근접 중복 검사는 미실행임. 팀원의 표본 마스크 시각 검토와 분할 최종 확정이 남아 T05는 검토 필요 상태임.
- 2026-11-18: [byhyun 001](eda/EXP_byhyun_001_preprocessing_check.md) 코드 셀 12개·오류 출력 0개·그림 3개를 확인함. train 조작 이미지 2,925장에서 이미지·마스크·정상 원본의 크기 불일치와 EXIF 방향 이상은 0개임. 샘플 200장에서 정상 원본은 모두 Q75·4:2:0, 조작본은 모두 Q100·4:2:0 JPEG임. ELA 후보·scale·Crop 크기·패딩 필요 여부는 제안이며, 임계값·학습 조건·ELA 최종 설정은 T06에서 확정해야 함. 마스크 밖이 원본과 크게 다른 이미지가 100장 중 20장이라 T05의 마스크 시각 검토가 필요함.
- 2026-11-20: [kimjihwan 001 U-Net 동작 확인](rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.md)([노트북](../notebooks/rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.ipynb))의 Colab 저장 출력을 확인함. 코드 셀 11개·오류 출력 0개·그림 3개임. torch 2.14.1+cu130·torchvision 0.29.1+cu130, A100에서 세 U-Net의 가중치 로드·학습·체크포인트 재로드·원본 해상도 추론·평가 함수 연결이 동작함. 몇 step만 학습한 동작 확인이라 모델 실험 표에 점수를 넣지 않음.
- 2026-11-20: [byhyun 002](eda/EXP_byhyun_002_preprocessing_padding_check.md) 코드 셀 4개·오류 출력 0개·그림 1개를 확인함. 실행번호는 1, 2, 6, 9로 오름차순이지만 연속이 아님. 수정된 입력 검사는 합성 입력에서 의도대로 동작했고, AutoSplice val 조작 이미지 361장 모두에서 32의 배수 우하단 패딩, 좌측 상단 보존, 패딩 영역 0, 마스크 복원이 일치함(패딩이 필요했던 이미지 250장). train·test·CocoGlide와 모델 출력 언패딩은 확인하지 않음. 평가 집계·임계값·학습 조건이 남아 T06은 완료가 아님.

## 모델 동작 확인 — 단일 이미지

아래 점수는 train 한 장의 실행 확인 결과임. 전체 테스트 평균과 구분하며 모델 순위 비교에 사용하지 않음. T12는 진행 중임.

| 실험·보고서 | 모델 | 데이터·이미지 | 평가 조건 | 조작/정상 수 | Pixel F1 | IoU | 정상 픽셀 오탐률 | 상태 | 노트북 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [EXP_kimjaehak_003_catnet_pretrained_check_singleImage](catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.md) | CAT-Net v2 | AutoSplice train, JPEG 100, 39406_0.jpg | 원본 256×374, 임계값 0.5, bilinear 복원 후 패딩 제거 | 1 / 0 | 0.906346 | 0.828732 | 미측정 | 완료: 단일 이미지 동작 확인 | [노트북](../notebooks/catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.ipynb) |

가중치 strict 로드의 누락·추가 키는 0개임. TP 8,105·FP 1,659·FN 16·TN 85,964를 확인함. 공통 코드·분할 버전은 기존 버전을 사용했다는 실행자 확인에 근거하며, 실행번호와 재현 정보의 한계는 개별 보고서에 기록함.
