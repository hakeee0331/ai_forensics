# 사전학습 가중치 준비

사전학습 가중치는 프로젝트 루트의 `models/pretrained/<모델명>/`에 둠. CAT-Net은 `models/pretrained/catnet/CAT_full_v2.pth.tar`를 사용함. 학습 결과는 Drive의 `AI_Forensics/project/models/checkpoints/catnet/`에 `<실험파일명>_best.pt`로 보관함. 공식 초기 가중치와 구분하며 [체크포인트 복사·해시 확인·재로드 안내](../../docs/catnet_training.md#체크포인트-보관재시작)를 따름.

## 공유 Drive 반영 — 필수

**로컬에 가중치를 추가하거나 변경하면, Colab 실행 전에 공유 Drive의 `AI_Forensics/project/models/pretrained/`에도 같은 상대 경로로 업로드해야 함.** `scripts/`와 마찬가지로 로컬과 Drive 사이의 자동 동기화는 없음. Git commit·push로 가중치가 Drive에 전달되지 않음.

| 구분 | CAT-Net 가중치 경로 |
| --- | --- |
| 로컬 프로젝트 기준 | `models/pretrained/catnet/CAT_full_v2.pth.tar` |
| 공유 Drive 기준 | `AI_Forensics/project/models/pretrained/catnet/CAT_full_v2.pth.tar` |
| Colab 마운트 후 | `/content/drive/MyDrive/AI_Forensics/project/models/pretrained/catnet/CAT_full_v2.pth.tar` |

1. 공식 배포처에서 사용할 가중치를 받아 모델별 폴더에 둠. CAT-Net은 [공식 저장소](https://github.com/mjkwon2021/CAT-Net)의 가중치 다운로드 안내를 따름.
2. 공유 Drive의 같은 위치에 업로드함. 이미 같은 파일이 준비돼 있으면 크기·SHA-256을 확인한 뒤 재사용함. 실행 중인 팀원이 있으면 교체 시점을 먼저 조율함.
3. 노트북에서 Drive를 마운트하고 파일 존재 여부를 확인함. 가중치를 `/content` 아래 실행용 경로로 복사하고 원본과 복사본의 SHA-256이 같은지 확인함.
4. 가중치 출처·파일명·파일 크기·SHA-256과 공식 코드 커밋 ID를 노트북에 기록함. 배포처가 기준 해시를 제공하면 함께 대조함. 직접 계산한 해시는 실행 파일 식별용이며 배포처 검증을 대신하지 않음.
5. 가중치를 변경한 경우 런타임 복사본을 갱신하고 모델에도 새 가중치를 다시 로드함. Drive 파일만 교체해도 메모리에 올라간 모델은 바뀌지 않음.

가중치 파일은 Git에 올리지 않음. 현재 `.gitignore`의 `*.pth`, `*.pt`, `*.tar` 등으로 제외하며, 안내 문서와 `.gitkeep`은 추적함. 새 형식의 가중치를 추가하면 Git 제외 여부를 확인해야 함.

이 문서는 준비 절차임. 파일이 실제로 업로드·복사됐는지와 모델 로드 성공 여부는 실행 출력으로 확인해야 함. 전체 실행 절차는 [노트북 실행 안내](../../docs/workflow.md)를 따름.
