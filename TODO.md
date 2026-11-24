# 작업 목록

상태: `미착수` / `진행 중` / `검토 필요` / `검증 필요` / `완료` / `보류`. 우선순위: `P0` 준비·기본 비교에 필수, `P1` 기본 실험, `P2` 후속 개선. 담당자가 정해지면 팀의 Git 식별자로 기입한다. 실험 번호는 이 표의 작업 ID와 별개다.

`검토 필요`는 준비된 자료·결과에 대한 사람의 검토와 합의가 남은 상태임. `검증 필요`는 실제 동작·조건 확인이 남은 상태이며 설정 확정이나 검증 완료를 뜻하지 않음.

## P0 — 준비

| ID | 작업 | 담당 | 상태 | 완료 조건 |
| --- | --- | --- | --- | --- |
| T01 | 프로젝트 구조·운영 규칙 구성 | kimjaehak | 완료 | 세 폴더와 모델·EDA 하위 폴더, 운영 문서, .gitignore 배치 |
| T02 | 공통 전처리·평가 함수 초안 | kimjaehak | 완료 | 이미지·마스크 읽기, 동일 위치 크롭, ELA, confusion counts·F1·IoU·오탐률 함수 제공 |
| T03 | Colab 기본 실행 환경 확정·검증 | kimjaehak | 완료 | 최신 기본 런타임 사용 규칙·실제 버전 기록·CAT-Net 추가 설치를 문서화하고 새 GPU 세션의 007 저장 출력 확인 |
| T04 | Git 운영 정책 확정 | 미정 | 완료 | 통합·작업 브랜치·병합·커밋 정책과 팀 작업 절차 명시 |
| T05 | 데이터셋 EDA·분할 확정 | seonghun | 완료 | 데이터·마스크·분할 검토와 확인된 교차 중복 기록, 기존 분할 유지 확정 |
| T06 | 공통 비교·평가 규약 확정 | 미정 | 검증 필요 | ELA 품질·배율·서브샘플링·처리 순서, 임계값·해상도·집계·빈 마스크 규칙, 학습 조건 합의 |
| T07 | 데이터셋별 로더·분할 연결 | kimjaehak | 완료 | 공통 ZIP 준비·데이터 경로·고정 분할 연결을 Colab에서 확인 |
| T08 | 첫 예시 작업 함께 진행 | kimjaehak | 완료 | 사용할 데이터 위치를 확인하고 첫 노트북을 작성·실행·기록 |
| T17 | 공통 전처리 실행 검증 | 에이전트 | 완료 | Pillow가 있는 환경에서 RGB·마스크 읽기, 크롭 정합성, ELA 오차 계산·자료형·클리핑 확인 |
| T18 | 초기 파일 이전·구조 점검 | 에이전트 | 완료 | 기존 파일·Git 메타데이터 보존, 구조·링크·제외 규칙 확인 |
| T19 | 제안서 계획과 실행 규약 대조·확정 | 미정 | 진행 중 | README의 대조표를 검토해 CAT-Net 파인튜닝 범위와 T05·T06의 설정을 확정하고 문서에 반영 |

## 현재 상태와 후속 작업 — 2026-11-22

### 실행·기록

- [001 평가 함수 예제](docs/eda/EXP_kimjaehak_001_evaluation_example.md): Colab 실행·출력 검토 완료. 실제 데이터 로드, 고정 분할 연결, 설명용 예측 10개 사례와 지표 계산을 확인함. 모델 성능은 측정하지 않음.
- [002 데이터 EDA](docs/eda/EXP_kimjaehak_002_dataset_eda.md): Colab 실행·출력 검토 완료. 이미지 14,160개·마스크 2,222개의 읽기·값·대응 크기 오류와 파일·RGB 해시 중복은 0개임. AutoSplice train 전체에서 256×256 크롭이 가능하지만 학습 크기는 미확정임.
- [003 CAT-Net 단일 이미지 확인](docs/catnet/EXP_kimjaehak_003_catnet_pretrained_check_singleImage.md): 모델 로드·train 한 장의 입력·추론·시각화·평가 완료. F1 0.906346, IoU 0.828732는 단일 이미지 결과이며 전체 성능이 아님.
- [004 CAT-Net 전체 테스트 평가](docs/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md): AutoSplice test·CocoGlide 전체 2,257장 집계와 그림 18개 검토 완료. CocoGlide F1 0.363874·IoU 0.287961·정상 픽셀 오탐률 0.166143이며 PNG→JPEG100·4:4:4 입력 조건과 한계를 기록함.
- 001·002·003·004·005·006·007은 저장 출력 검토를 마쳐 보존함. kimjaehak의 다음 새 실험 번호는 008임. 새 파일 작성 직전에 번호 충돌을 확인함. 실행 환경·코드 버전·측정값·검증 한계는 각 보고서에 기록함.
- [byhyun 001 전처리 실데이터 검증](docs/eda/EXP_byhyun_001_preprocessing_check.md): Colab 저장 출력 검토 완료. AutoSplice에서 ELA·크롭 처리와 평가 규칙 관련 개수를 확인하고 ELA 후보와 크롭 크기를 제안함. 모델 성능은 측정하지 않음.
- [byhyun 002 전처리 패딩·입력 검증](docs/eda/EXP_byhyun_002_preprocessing_padding_check.md): Colab 저장 출력 검토 완료. 수정된 입력 검사와 `pad_image`·`unpad_image`를 합성 입력과 AutoSplice val 조작 이미지 361장에서 확인함. 모델 성능은 측정하지 않음. byhyun의 새 실험 번호는 003임.
- [kimjihwan 001 U-Net 동작 확인](docs/rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.md): Colab 저장 출력 검토 완료(2026-11-20). ResNet-50 U-Net의 3·6채널 입력, 작은 배치 학습, 체크포인트 재로드, 원본 해상도 추론과 평가 함수 연결이 A100에서 모두 동작함. 학습 설정은 임시값이며 기본 실험·성능 측정이 아님.
- [kimjihwan 002 RGB U-Net·손실 비교](docs/rgb_unet/EXP_kimjihwan_002_rgb_unet_loss_compare.md): Colab(L4) 저장 출력 검토 완료(2026-11-24). BCE·이미지별 Dice·BCE+Dice의 val F1 차이가 0.003 이내이며 규칙대로 `bce_dice`를 선택함. AutoSplice JPEG100 F1 0.969, JPEG90 0.279, JPEG75 0.005, CocoGlide 정상 픽셀 오탐률 0.970으로 압축 이력에 의존한 것으로 보임.
- [kimjihwan 003 ELA U-Net](docs/ela_unet/EXP_kimjihwan_003_ela_unet_baseline.md): Colab(L4) 저장 출력 검토 완료(2026-11-24). AutoSplice JPEG100 F1 0.957, JPEG90 0.001, JPEG75 0.008, CocoGlide 정상 픽셀 오탐률 0.941로 RGB보다 나은 점이 없음.
- [kimjihwan 004 RGB+ELA U-Net](docs/rgb_ela_unet/EXP_kimjihwan_004_rgb_ela_unet_baseline.md): Colab(L4) 저장 출력 검토 완료(2026-11-24). AutoSplice JPEG100 F1 0.972로 세 U-Net 중 가장 높으나 차이는 작고, JPEG90 0.005·JPEG75 0.008·CocoGlide 정상 픽셀 오탐률 0.976임. 세 U-Net 모두 JPEG 재압축과 CocoGlide에서 일반화하지 못해 JPEG 증강(T14)의 근거로 공유함.
- [kimjihwan 006 압축 흔적 측정](docs/eda/EXP_kimjihwan_006_compression_trace_check.md): Colab CPU 저장 출력 검토 완료(2026-11-25). AutoSplice JPEG100 조작본은 마스크 밖에만 Q75 압축 흔적이 남아 학습 없이 위치를 찾을 수 있음(AUC 0.92). CocoGlide에는 격자 흔적이 없고 마스크 밖이 원본과 같은 부분 편집임.
- [kimjihwan 005 JPEG 증강](docs/rgb_ela_unet/EXP_kimjihwan_005_rgb_ela_unet_jpeg_aug.md): Colab(T4) 저장 출력 검토 완료(2026-11-25). AutoSplice JPEG90·75 F1이 0.005·0.008에서 0.787·0.794로 회복됐지만 정상 픽셀 오탐률이 0.323으로 올랐고 CocoGlide JPEG100은 위치 정보가 없음. Drive 용량 초과로 epoch 10 체크포인트를 잃음(공유 폴더 005 파일은 epoch 3).
- [kimjihwan 007 정상 이미지 포함](docs/rgb_ela_unet/EXP_kimjihwan_007_rgb_ela_unet_grid_break.md): Colab(T4) 저장 출력 검토 완료(2026-11-25). 의도한 격자 깨기가 적용되지 않아 사실상 "005 + 정상 이미지"임. AutoSplice 정상 오탐률 0.051, CocoGlide JPEG100 정상 오탐률 0.922.
- [kimjihwan 008 격자 깨기](docs/rgb_ela_unet/EXP_kimjihwan_008_rgb_ela_unet_grid_break_fixed.md): Colab(T4) 저장 출력 검토 완료(2026-11-25). 007과 격자 깨기만 다르며, CocoGlide JPEG100 정상 오탐률 0.922→0.527, 쌍 차이 AUC 0.514→0.604로 실행 전에 정한 기준을 넘음. AutoSplice JPEG100 F1은 0.933→0.835. 탐색적 결과임. kimjihwan의 다음 새 실험 번호는 009임.
- [seonghun 001 근접 중복 검사](docs/eda/EXP_seonghun_001_near_duplicate_check.md)·[002 CNN 특징 근접 중복 검사](docs/eda/EXP_seonghun_002_near_duplicate_feature_check.md): Colab 저장 출력 검토 완료(2026-11-23). 서로 다른 split 사이 중복은 46217(train)–54313(val) 1쌍, train 내부 중복 9쌍을 찾음. 분할 CSV는 변경하지 않음. seonghun의 다음 새 실험 번호는 004임.
- [seonghun 003 JPEG 저장 이력 확인](docs/eda/EXP_seonghun_003_jpeg_history_check.md): Colab 저장 출력 검토 완료(2026-11-23). AutoSplice 정상 원본 2,273장은 모두 Q75, 조작본은 폴더 이름의 품질(100·90·75)과 모두 일치하며 4:2:0·표준 테이블임. CocoGlide는 모두 PNG임. 정상·JPEG100 조작본이 저장 품질만으로 구분되므로 학습·평가 조건 논의가 필요함.
- [005 출력부 전이학습](docs/catnet/EXP_kimjaehak_005_catnet_transfer_learning.md)·[006 전체 파인튜닝](docs/catnet/EXP_kimjaehak_006_catnet_finetuning.md): 2026-11-22 A100 저장 출력 검토 완료. 각각 코드 셀 15개·오류 0개·그림 13개·테스트 2,257행을 확인함. 005는 epoch 15 선택, JPEG100 개선과 JPEG75·CocoGlide 악화를 함께 기록함. 006은 5 epoch 학습 후 개선 없이 epoch 0 선택으로 학습 개선에 실패함. 체크포인트 재로드 오차는 둘 다 0이며 Drive 보관·팀원 시각 검토 확인은 남아 있음. [실행·보관 안내](docs/catnet_training.md)를 따름.
- 2026-11-23 기준 005·006 체크포인트는 작성자 확인으로 Drive 미업로드 상태임. 원본 파일이 남아 있으면 기존 경로로 복사해 해시를 검증함. 다음 학습 노트북부터 [실행 안내](docs/workflow.md#학습-체크포인트-보관)의 모델별 경로와 자동 보관 절차를 반영해야 함.

### 로컬 데이터 준비

- [data/README.md](data/README.md)에 ZIP·해제 폴더 배치, 공통 로더 경로, 고정 분할·해시 확인과 로컬 실행 기록 방법을 정리함. `data/.gitkeep`과 안내 문서만 Git 추적 대상으로 두며 실제 데이터는 제외함.
- 기존 Colab 노트북은 보존함. 로컬용 노트북·환경 구성과 실제 실행 검증은 아직 하지 않음.

### 사전학습 가중치 준비 — 2026-11-20

- 사전학습 가중치 위치를 `models/pretrained/<모델명>/`으로 정함. 로컬 추가·변경 시 공유 Drive의 `AI_Forensics/project/` 아래 같은 경로에도 업로드해야 함. [준비 안내](models/pretrained/README.md)에 복사·해시 확인·재로드 절차를 기록함.
- CAT-Net 대상 파일은 `catnet/CAT_full_v2.pth.tar`임. 003 저장 출력에서 Drive 접근·복사 해시 일치·strict 로드·단일 이미지 추론을 확인함. 학습 체크포인트는 Drive의 `AI_Forensics/project/models/checkpoints/catnet/`에 실험 파일명으로 보관함. 예측 이미지·지표 등 나머지 저장 구조(T16)는 계속 보류함.

### 준비 항목별 상태

- **T03 — 완료 (2026-11-24):** [007 보고서](docs/eda/EXP_kimjaehak_007_colab_environment_check.md)에서 Colab Tesla T4의 기본 패키지 버전 유지, 세 U-Net의 갱신·재로드·평가 연결과 CAT-Net JPEG 추론·출력부 갱신을 확인함. H100은 미검증임.
- **T04 — 완료:** [기여 규칙](CONTRIBUTING.md#작업-브랜치)에 `main` 통합, 작업 브랜치 유지·순차 작업, 다른 팀원 1명 승인, 지정 담당자의 일반 병합을 명시함. 커밋 접두어 `exp`·`feat`·`docs`·`fix`와 PR의 변경 내용·확인 결과·남은 사항 형식을 확정함. 실제 운영 준비는 아래에서 별도로 확인함.
- **T05 완료 (2026-11-24).** seonghun이 train 마스크 표본 9장과 근접 중복을 검토함. 팀은 확인된 train–val 중복 1쌍의 범위가 작다고 판단해 기존 seed 42 분할 유지를 확정함. train 내부 중복 9쌍도 유지함. [분할 결정](scripts/splits/README.md#분할-유지-결정--2026-11-24)
- 저장 품질 차이(정상 Q75·JPEG100 조작본 Q100)의 학습·평가 영향과 학습용 품질·품질별 평가 보고는 T06에서 논의함. JPEG 증강은 기본 비교 이후 T14에서 검토함. [JPEG 저장 이력](docs/eda/EXP_seonghun_003_jpeg_history_check.md)
- **T06 — 검증 필요:** byhyun 001의 확인 결과를 바탕으로 팀 합의를 거쳐 ELA 설정(quality=90, scale=15, subsampling=2), 처리 순서(원본 ELA 선계산 → 256×256 크롭 → 동일 좌우반전), 평가 시 32의 배수 우하단 제로 패딩·언패딩 규칙을 확정함. 나머지 평가 임계값·집계·빈 마스크 처리, 학습 조건은 팀 합의로 확정해야 함. seonghun 003에서 AutoSplice 전체 split의 정상 Q75·JPEG100 조작본 Q100을 확인함. 테스트 데이터로 설정을 선택하지 않음.
- **T07 — 완료:** AutoSplice 원본 ID 기준 80/10/10 고정 분할과 CocoGlide 외부 테스트 구성을 공통 로더에 연결함. ZIP 준비·이미지·마스크 경로·분할 연결을 001·002의 Colab 출력에서 확인함. 완료 범위는 현재 `datasets.py`의 데이터 준비·경로 목록 제공까지임. 프레임워크별 Dataset·DataLoader 구현·검증은 T09~T12의 모델 실험 준비에서 진행하며, 데이터 내용·분할 검토는 T05에 기록함.
- **T12 — 진행 중:** 003 단일 이미지 확인에 이어 [004](docs/catnet/EXP_kimjaehak_004_catnet_pretrained_evaluation.md)에서 `scripts/catnet.py`의 준비·로드·입력 구성·추론을 사용해 AutoSplice test·CocoGlide 2,257장 평가를 완료함. 정상·조작 이미지와 AutoSplice JPEG 100·90·75를 분리 집계하고 시각화 18개를 검토함. CocoGlide PNG는 노트북에서 JPEG100·4:4:4로 변환함. 공식 코드·가중치·catnet.py 해시는 출력에서 확인했으나 다른 공통 코드·분할 CSV의 런타임 해시는 저장되지 않음. 사전학습 데이터와의 중복 검토·재현 정보 보완은 남아 있음. 005·006의 학습·역전파 실행 결과는 T21·T22로 구분함. 003·004의 미기록 런타임 해시를 후속 실행 해시로 소급 확정하지 않음.
- **T19 — 진행 중:** 사용자 요청에 따라 005는 출력부만 학습, 006은 전체 파인튜닝으로 비교 범위를 명시함. 같은 초기 가중치·데이터·손실·평가 조건으로 실행했으며 공통 설정 서명·환경 일치를 확인함. 006은 학습 개선에 실패했으므로 안정성 후속 점검이 필요함. T05의 기존 분할 유지 결정은 반영했으며 학습값과 T06의 최종 팀 합의는 남아 있음.

### Git 운영 준비

- 초기 파일은 여섯 커밋으로 등록했고, 로컬 데이터 안내를 포함한 `72c35f0`까지 원격 `main`에 반영됨.
- 팀원 접근 권한 확인, 작업 브랜치 생성, 병합 담당자 지정과 clone 안내는 운영 준비로 남음. T04의 정책 문서화 완료와 구분함.

### 공통 함수 검증 상태

- T02 완료는 함수 초안 작성을 뜻함. 팀원 검증이나 공통 전처리·평가 규약 승인까지 완료된 것은 아님.
- 평가 함수는 2×2 이진 마스크 256가지 조합, 분모 0 처리와 잘못된 입력을 검사함. 현재 함수는 개별 지표만 계산하며 임계값 적용·정상/조작 구분·이미지별 평균은 노트북에서 처리함.
- T17은 합성 입력의 RGB·마스크 로드, 크롭 정합성·복사본 독립성, ELA 27개 설정 조합의 계산 검증을 완료한 상태임. byhyun 001에서 Colab 실제 데이터 크롭·ELA 동작을 확인하고 팀 합의로 전처리·패딩 공통 규약을 확정함. 수정된 코드의 팀원 검증은 진행 중임. [전처리 안내](docs/preprocessing.md)의 입력 제한과 검증 범위를 확인함.
- 전처리의 남은 입력 검사 항목(scale의 불리언·문자열·복소수 거부, NumPy 정수 전경값 허용)을 수정하고, 평가용 우하단 제로 패딩·언패딩 함수(pad_image, unpad_image)를 추가해 합성 입력으로 동작을 확인함.
- ZIP 준비 함수는 합성 ZIP으로 해시 불일치·캐시 재사용·손상·누락·해제 중단 처리를 검사함. 실제 데이터의 최초 해제는 001, 기존 해제 파일 재사용은 002의 Colab 출력에서 확인함. 004에서도 두 ZIP의 해시 확인·압축 해제 완료 출력을 확인함.
- 공통 코드를 수정하면 다음 실행 전에 공유 Drive에도 반영하고 새 커널에서 불러와야 함. [필수 업로드 절차](README.md#공통-코드-수정-후-drive-업로드--필수)를 따름.

## P1 — 기본 실험

| ID | 작업 | 담당 | 상태 | 완료 조건 |
| --- | --- | --- | --- | --- |
| T09 | RGB U-Net 기본 실험 | kimjihwan | 검토 필요 | 확정한 공통 조건으로 실행하고 노트북·보고서·점수표 기록 |
| T10 | ELA U-Net 기본 실험 | kimjihwan | 검토 필요 | RGB 기본 실험과 비교 가능한 조건으로 실행·기록 |
| T11 | RGB+ELA U-Net 기본 실험 | kimjihwan | 검토 필요 | 같은 이미지에서 RGB·ELA를 구성해 실행·기록 |
| T12 | CAT-Net 사전 학습 모델 검증 | kimjaehak | 진행 중 | 공식 입력·가중치·학습 데이터 중복 요건 확인 후 실행·기록 |
| T13 | 기본 결과 비교·정성 분석 | 미정 | 미착수 | 조건별 점수와 성공·실패 사례·모델 분석을 보고서에 정리 |
| T21 | CAT-Net 출력부 전이학습 | kimjaehak | 검토 필요 | 005 학습·epoch 15 선택·테스트·보고서 갱신 완료. Drive 체크포인트 보관·팀원 시각 검토 확인 필요 |
| T22 | CAT-Net 전체 파인튜닝 | kimjaehak | 검토 필요 | 006 실행·보고서 갱신 완료. 학습 개선 실패로 epoch 0 평가. Drive 보관 확인 및 train·val 기반 안정성 후속 실험 검토 |

## P2 — 후속 작업

| ID | 작업 | 담당 | 상태 | 완료 조건 |
| --- | --- | --- | --- | --- |
| T14 | JPEG 증강 | kimjihwan | 검토 필요 | RGB+ELA U-Net에 품질 70~100 재압축 증강(005, 제안서 4-3)을 적용해 004와 비교함. 추가로 정상 이미지 포함(007)·압축 격자 깨기(008)를 실험함. 팀 검토와 보고서 확인 필요 |
| T15 | 학습·전처리 조건 개선 | 미정 | 보류 | 기준 실험과 변경점을 명시한 새 실험으로 비교 |
| T16 | 모델 출력·지표 저장 구조 검토 | 미정 | 보류 | CAT-Net 체크포인트 Drive 경로는 안내에 기록함. 예측 이미지·지표 JSON 등 나머지 저장 위치·재현 방법·Git 제외 범위는 별도 합의 |
| T20 | 에이전트의 VS Code·Colab 실행 연동 | 미정 | 보류 | 현재 수동 실행 흐름을 확인한 뒤 원격 코드 전달·셀 실행·출력 회수 자동화 범위를 검토 |

새 작업은 ID, 우선순위, 담당, 상태, 완료 조건을 붙여 추가한다. 수행한 작업만 완료로 표시하고 실험이 생기면 해당 노트북·보고서 링크도 남긴다.