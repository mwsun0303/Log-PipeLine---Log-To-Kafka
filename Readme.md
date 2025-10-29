# Log PipeLine - Log To Kafka

## 프로젝트 개요

**Log To Kafka** 는 로그 파일 내에서  
특정 **Log Trigger (Trigger Keywords)** 또는 **Exception Trigger (Exception Keywords)** 를 감지하고,  
해당 줄부터 최대 **30줄(현재 줄 + 다음 29줄)** 을 하나의 그룹으로 묶어 **Kafka Topic** 으로 Producing하는  
경량형 **Log Monitoring & Streaming Tool** .

서버별로 배포 후 로그 경로만 지정하면,
여러 서버의 로그를 Server → Kafka → PostgreSQL로 중앙 관리가 가능  
**deploy.sh** 를 통해 Build & Deploy

---

## 버전 정보

| 구성 요소 | 버전 |
|------------|-------|
| Python     | 3.10  |
| OS Base    | Debian slim |
| Docker     | 최신 (23.x 이상 권장) |
| Kafka      | 3.8 |
| 앱 버전    | v1.0.0 |

---

## 디렉터리 구조

```bash
project-root/
├── app.py                # Main Application 
├── requirements.txt      # Python Dependency
├── Dockerfile            # Docker File
├── deploy.sh             # Build & Deploy Script
└── README.md             
