# 모델 구현 패키지 사용 제안

작성일: 2026-11-17  
2026-11-23 갱신. 실행 환경은 [README의 최신 Colab 기본 런타임 사용 규칙](../README.md#colab-기본-실행-환경)을 따름. 아래는 제안 당시의 근거와 검증 항목임. 2026-11-24에 007의 Tesla T4 저장 출력으로 환경 검증을 마침.

## 제안 내용

RGB U-Net, ELA U-Net, RGB+ELA U-Net은 **PyTorch와 torchvision을 공통으로 사용**하는 것을 제안함. 모델 구조와 학습 절차를 하나의 기준 구현에서 출발하도록 맞추고, 입력 구성에 따른 차이를 비교하고자 함.

CAT-Net도 공식 PyTorch 구현을 사용하되, 전용 전처리·가중치·의존성에 맞춰 실행 환경을 별도로 확인함. 네 모델의 딥러닝 프레임워크는 PyTorch로 맞출 수 있지만, 모든 모델을 같은 패키지 버전으로 실행할 수 있는지는 검증이 필요함.

이 문서는 패키지 선택을 위한 제안이며 설치나 학습을 실행한 기록이 아님. 기존 실험 결과와 팀 필수 환경을 변경하지 않음.

## 패키지를 맞추려는 이유

프로젝트의 핵심 질문은 RGB 대신 ELA를 사용하거나 두 입력을 결합했을 때 검출 성능이 어떻게 달라지는지임. 모델마다 프레임워크와 라이브러리가 다르면 입력 외에도 모델 구조·초기화·손실 계산·최적화 설정이 달라질 수 있음.

예를 들어 Adam의 기본 epsilon은 PyTorch가 1e-8, Keras가 1e-7임. 이 차이만으로 성능 차이가 크다고 단정할 수는 없지만, 같은 이름의 최적화기를 썼다는 사실만으로 같은 설정이라고 볼 수는 없음. [PyTorch Adam](https://docs.pytorch.org/docs/2.15/generated/torch.optim.Adam.html), [Keras Adam](https://keras.io/api/optimizers/adam/)

같은 프레임워크를 쓰면 코드를 공유하고 차이를 검토하기 쉬움. 다만 PyTorch를 통일하는 것만으로 공정한 비교가 보장되지는 않으며, 아래 모델·학습·평가 조건도 함께 맞춰야 함.

## 공통으로 사용할 패키지

| 패키지 | 역할 | 사용 제안 |
| --- | --- | --- |
| torch | 모델 정의, 텐서 연산, 자동 미분, 손실 계산, 최적화, 학습·추론 | 세 U-Net의 공통 학습 프레임워크로 사용함 |
| torchvision | 사전학습 ResNet-50 구조와 가중치 | 세 U-Net의 인코더를 같은 구현·가중치 식별자로 맞춤 |
| numpy | 이미지·마스크 배열 처리, 공통 지표 계산 | 기존 preprocessing.py·evaluation.py와 함께 사용함 |
| Pillow | 이미지 읽기, RGB 변환, ELA 내부 JPEG 재압축 | 기존 전처리 함수를 사용해 읽기·재압축 방식을 통일함 |
| pandas | 분할 목록 확인, 결과 표 정리 | EDA와 보고용 표에 사용함 |
| matplotlib | 이미지·마스크·예측·학습 곡선 시각화 | 노트북에 확인할 그림을 남기는 데 사용함 |

torchvision은 ResNet-50과 ImageNet 사전학습 가중치를 제공함. 완성된 우리 프로젝트용 U-Net을 그대로 제공한다는 의미는 아니며, 인코더의 특징을 받아 원본 해상도의 예측을 만드는 디코더를 연결해야 함. [torchvision ResNet-50](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html)

ZIP·파일 경로·해시 처리에는 기존처럼 Python 표준 라이브러리인 zipfile, pathlib, hashlib 등을 사용함. Drive 마운트는 Colab의 google.colab을 사용함.

TensorFlow·Keras를 공통 필수 의존성에 추가할 필요는 없음. 별도 U-Net 라이브러리나 학습 프레임워크를 추가하고 싶다면, 세 U-Net에 같은 구현을 적용할 수 있는지와 의존성을 먼저 검토함.

## 세 U-Net의 구현 방식

| 모델 | 입력 | 공통으로 유지할 부분 |
| --- | --- | --- |
| RGB U-Net | RGB 3채널 | 인코더·디코더의 기본 구조, 손실, 학습·검증·평가 절차 |
| ELA U-Net | ELA 3채널 | RGB U-Net과 같은 기준 구현 |
| RGB+ELA U-Net | RGB와 ELA를 결합한 6채널 | 입력층의 채널 확장 외에는 같은 기준 구현 |

RGB U-Net 기준 노트북을 먼저 만들고 검증한 뒤, 해당 코드를 바탕으로 나머지 두 모델을 작성하는 방식을 제안함. 모델·손실·학습 반복문은 기존 운영 규칙대로 노트북에 두고, 공통 데이터 처리·ELA·평가 함수는 scripts에서 가져옴.

기본 비교 전에 다음 항목을 명시해야 함.

- 인코더의 정확한 사전학습 가중치와 디코더 구조.
- RGB·ELA 입력 정규화와 6채널 입력층의 가중치 초기화 방식. 제안서의 RGB 가중치 복사 방식을 어떻게 적용할지 기록함.
- BCE·Dice의 계산식·평균 방식·결합 비중과 Adam의 설정.
- 데이터 분할, 배치 크기, 시드, 크롭·반전, 학습 예산, 조기 종료·체크포인트 선택 기준.
- 예측 확률 변환, 평가 해상도·임계값·이미지별 집계 방식.

사전학습 모델의 분류용 전처리를 그대로 적용해 이미지 크기를 바꾸지 않도록 주의함. 우리 프로젝트의 크롭·ELA·정규화 순서는 [전처리 사용 안내](preprocessing.md)와 T06에서 정한 조건을 따름.

공통 평가 함수에는 각 프레임워크의 텐서를 그대로 넘기기보다 CPU의 NumPy 배열로 변환하고, 이미지마다 동일한 임계값·집계 규칙을 적용함. 학습용 미분 가능한 Dice 손실은 평가용 NumPy 함수와 별도로 노트북에서 구현함.

## CAT-Net은 공식 구현을 기준으로 준비

CAT-Net 공식 저장소는 PyTorch 구현과 사전학습 가중치를 제공함. 공식 README의 환경 예시는 Python 3.6, torch 1.1.0, torchvision 0.3.0을 사용함. 이는 공식 저장소의 안내를 확인한 것이며, 이 구버전을 현재 팀 표준으로 채택하자는 뜻은 아님. [CAT-Net 공식 저장소](https://github.com/mjkwon2021/CAT-Net)

공식 requirements에는 torch_dct, jpegio, Cython, pyyaml, yacs, tqdm, pillow, opencv-python, tensorboardX, matplotlib, seaborn 등이 포함돼 있음. 이 목록은 CAT-Net 의존성이므로 세 U-Net의 기본 환경에 모두 추가하지 않음. 003·004에서 추론에 사용한 패키지 조합의 Colab 동작은 확인했으나, 이 requirements 전체와 학습 환경의 호환성은 별도 검증이 필요함. [공식 requirements](https://github.com/mjkwon2021/CAT-Net/blob/main/requirements.txt)

CAT-Net 담당자는 다음을 확인한 뒤 실행 환경을 기록함.

1. 사용할 공식 코드 버전과 CAT_full_v2 가중치를 특정함.
2. JPEG의 DCT 계수·양자화 테이블을 읽는 전처리와 추가 패키지 설치를 확인함.
3. 실제 샘플의 추론과 예측·정답의 공간 정합성을 확인함. 파인튜닝 범위가 확정되면 학습도 별도로 점검함.
4. 최신 Colab에서 수정이 필요하면 코드 변경 사항과 의존성 버전을 기록함. 같은 환경에서 실행하기 어려우면 별도 Colab 세션·환경으로 운영함.

CAT-Net 환경이 달라도 공통 테스트 목록과 평가 지표는 맞춰야 함. 전처리와 환경 차이는 보고서에 기록하고, 추론 속도 비교에서는 하드웨어·입력 크기·측정 범위를 함께 통제해야 함.

## 새 런타임에서 확인할 항목

2026-11-23부터 기본 비교에는 Colab 최신 GPU 런타임의 기본 패키지를 사용함. 실제 사용 버전과 CAT-Net 추가 설치 절차는 [README](../README.md#colab-기본-실행-환경)에 기록함. 세 U-Net의 A100 동작은 kimjihwan 001, CAT-Net의 A100 학습·재로드는 005·006에서 확인함. 006의 학습 안정성은 T22에서 다룸.

[007 환경 검증 보고서](eda/EXP_kimjaehak_007_colab_environment_check.md)에서 새 Colab 세션의 다음 출력을 확인함.

- 추가 패키지 설치 전후 기본 패키지 버전, 실제 GPU·CUDA와 공통 코드 해시.
- 세 U-Net의 사전학습 가중치 로드, RGB·ELA·RGB+ELA 입력별 출력 크기·자료형, 작은 배치의 순전파·역전파·갱신.
- U-Net 임시 체크포인트 재로드 전후 예측 대조와 공통 평가 함수 연결.
- CAT-Net 공식 가중치 로드, JPEG 입력·추론과 출력부의 작은 배치 갱신.

## 기존 작업 방식과 연결

팀원은 로컬 노트북을 VS Code에서 열고 Colab 원격 커널로 실행한 뒤, 출력이 포함된 파일을 저장함. 공통 코드 변경 시에는 [Drive 업로드 절차](../README.md#공통-코드-수정-후-drive-업로드--필수)를 따름. 보고서는 저장된 출력을 기준으로 작성함.

현재 완료된 [평가 함수 예제](eda/EXP_kimjaehak_001_evaluation_example.md)는 데이터 로드와 NumPy 기반 평가 사용법을 확인한 기록임. PyTorch 모델 학습이나 CAT-Net 실행 검증은 포함하지 않음.

이 제안의 패키지 선택·환경 검증은 [TODO](../TODO.md)의 T03, 모델·학습·평가 조건 합의는 T06과 연결함. 2026-11-24에 007 출력 검토 후 T03을 완료 처리함.
