# Colab 기본 GPU 런타임 검증

작성자 kimjaehak · 실행·저장 출력 검토일 2026-11-24 · 상태 완료 · T03

[007 노트북](../../notebooks/eda/EXP_kimjaehak_007_colab_environment_check.ipynb) · [U-Net 기준 보고서](../rgb_unet/EXP_kimjihwan_001_unet_pipeline_check.md) · [CAT-Net 기준 보고서](../catnet/EXP_kimjaehak_005_catnet_transfer_learning.md)

## 목적과 범위

최신 Colab 기본 GPU 환경에서 세 U-Net과 공식 CAT-Net이 동작하는지 확인함. 시드 42로 만든 256×256 합성 JPEG 한 장과 사각형 마스크를 사용함. 데이터 ZIP·분할·모델 성능 평가는 해당 없음. 세 U-Net은 ImageNet ResNet-50 가중치로 시작해 입력별로 한 번 갱신하고, 런타임 임시 파일의 재로드 예측과 평가 함수 연결을 확인함. CAT-Net은 공식 JPEG 추론과 출력부 한 번 갱신을 확인함. 최선 모델 선택과 Drive 학습 체크포인트 보관은 해당 없음.

## 실행 환경과 재현 정보

- 실행 시작 시각 2026-11-24 11:05:18 KST. Colab 런타임 태그 `release-colab-external-images_20261118-060058_RC00`, Python 3.13.16, Tesla T4 (PyTorch 표시 14912 MB), CUDA 13.0, cuDNN 92800.
- 추가 패키지 설치 전후 6개 버전 일치. PyTorch 2.14.1+cu130, torchvision 0.29.1+cu130, NumPy 2.4.6, Pillow 11.3.0, pandas 2.2.3, matplotlib 3.10.0.
- 설치 후 pyjpegio 0.3.0, yacs 0.1.8, torch-dct 0.1.6, PyYAML 6.0.3, opencv-python 5.0.0.93, tqdm 4.67.3.
- Drive 공통 코드 5개 파일의 import 경로와 SHA-256을 확인함. 저장 출력의 해시는 기준 커밋 `de0bb27607f5821c94f9cb21c2ea9854da181530`에서 사용한 파일과 일치함. 파일별 해시는 노트북 2절에 기록함.
- CAT-Net 공식 코드 `5eb85900b0e72423c95a8d41bc835b86c8671f8a`, 공식 가중치 915,503,873바이트, SHA-256 `f82aaafdd1142775231feedcea0bb7027f7370561d9e8d107465454001865989`.

## 저장 출력 검토 — 2026-11-24

코드 셀 6개, 실행번호 1~6, 오류 출력 0개를 확인함. 표와 그림 없이 텍스트 출력으로 검증함. 실행 전 런타임 초기화 여부와 드라이버 버전은 저장 출력에서 확인되지 않음.

| U-Net 입력 | 배치 크기·채널·높이·너비 | 1-step 점검 손실 | 재로드 예측 최대 절대 오차 | 평가 함수 연결 |
| --- | --- | ---: | ---: | --- |
| rgb | (1, 3, 256, 256) | 0.759149 | 0.0 | 통과 |
| ela | (1, 3, 256, 256) | 0.874532 | 0.0 | 통과 |
| rgb_ela | (1, 6, 256, 256) | 0.606930 | 0.0 | 통과 |

세 입력 모두 ImageNet 가중치 로드, 유한한 손실·출력부 기울기, SGD 갱신 후 가중치 변화, 새 모델에 체크포인트 재로드, 혼동행렬·F1·IoU 함수 호출을 확인함.

CAT-Net은 JPEG 256×256 한 장에서 입력 (24, 256, 256), 양자화 테이블 (1, 8, 8)을 구성하고 원본 크기의 유한한 확률맵을 반환함. 출력부의 기울기·갱신 검사를 통과했고 점검 손실은 0.031166임. 공식 코드에서 텐서 생성 성능 경고 1건과 `upsample` 사용 중단 예정 경고 3건이 출력됨.

T03의 Colab 기본 GPU 환경 검증을 완료함. 007에서 확인한 범위는 T4의 합성 입력 동작이며, H100 동작과 본 학습 성능은 미측정임.

실행자 저장본 SHA-256은 `824b7b091f1ee1a2013e7bfce1bc444d8fde33ef6c4854c367b3c74ebd570696`이며, 첫 Markdown 셀에 완료 상태를 반영한 보존본 SHA-256은 `ce1511a058e47a2b3ce22f2090c0aa712236be6d9c78e7cb56faeb7b01045ecc`임.
