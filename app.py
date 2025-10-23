import os
import time
import json
import threading
from kafka import KafkaProducer
from datetime import datetime, timedelta, timezone

# Time Zone
KST = timezone(timedelta(hours=9))

# Log Directory Full Path
LOG_DIRS = [
    "[Log Path_1]",
    "[Log Path_2]"
    ...
]

# Env (Data Value)
instance_alias = "prod-server"
public_ip = "0.0.0.0"
project = "api"
was_no = "1"

# Kafka Config
# Topic Name 
kafka_topic = "log_topic_s3"  
# Producer Config
producer = KafkaProducer(
    bootstrap_servers='[Host IP]:9092',
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="[UserName]",
    sasl_plain_password="[Password]",
    value_serializer=lambda v: json.dumps(v).encode('utf-8') # Json 형태로 Kafka로 Producing
)

# Kafka Connect Test
def check_kafka_connection():
    try:
        producer.flush(timeout=10)
        print("[INFO] Kafka Connect Success")
        return True
    except Exception as e:
        print(f"[ERROR] Kafka Connect Fail: {e}")
        return False

# tail -f Log 추적
def tail_f(filepath):
    try:
        with open(filepath, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield line.strip()
    except Exception as e:
        print(f"[ERROR] tail_f Faile: {filepath}, {e}")

# Log Processing / Keyword Catch
def process_log_file(path):
    line_iter = tail_f(path)
#    trigger_keywords = [" info ", " error ", " warn ", " debug "]          # Log Keyword / dev (debug 포함)
    trigger_keywords = [" info ", " error ", " warn "]                      # Log Keyword / prod
    exception_keywords = ["exception", "traceback", "caused by", "at "]     # Application Exception Keyword

    for line in line_iter:                                                  # Line Check Loop
        lower_line = f" {line.lower()} "                                    # 키워드 소문자 변경 공백 처리
        matched_trigger = None                                              # Trigger Match Status / Default : None
        is_exception = any(kw in lower_line for kw in exception_keywords)   # Line에 Keyword 포함 체크 체크될 경우 True 반환

        for keyword in trigger_keywords:                                    # True 반환 시 Trigger 종류 Check / Log Keyword Check Loop 동작
            if keyword in lower_line:                                       # 일치 Trigger 존재 시 
                matched_trigger = keyword.strip().upper()                   # 공백 제거 후 Trigger 값 저장
                break                                                       # 반복문 종료

        if matched_trigger or is_exception:                                 # Log Keyword에서 Trigger Check가 되지 않은 경우
            grouped_lines = [line]                                          # 해당 Keyword줄부터 30줄을 Groupd_lines List에 저장
            try:
                for _ in range(29):  # Line 
                    next_line = next(line_iter)
                    grouped_lines.append(next_line)
            except StopIteration:                                           # 30줄 이전에 파일의 내용이 끝날 경우, Exeption 처리 Pass
                pass

            log_data = {                                                    # Log Data Producing 규격
                "project": project,
                "log_trigger": matched_trigger if matched_trigger else "EXCEPTION",
                "log_message": "\n".join(grouped_lines),
                "timestamp": datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "log_path": path,
                "instance_alias": instance_alias,
                "public_ip": public_ip,
                "was_no": was_no
            }

            try:
                producer.send(kafka_topic, log_data)                        # Topic 생성
                print(f"[Kafka] Log Send Success: {kafka_topic}")
            except Exception as e:
                print(f"[Kafka Error] Send Fail !!: {e}")

def main():                                                                 # Main 
    print("[INFO] Log Monitoring Start")

    if not check_kafka_connection():                                        # Kafka 연결 호출
        print("[ERROR] Kafka Connection Fail - Shutdown")
        return

    log_files = []
    for d in LOG_DIRS:
        if not os.path.exists(d):
            print(f"[WARNING] Log Directoryt is Not exist: {d}")
            continue
        log_files += [
            os.path.join(d, f) for f in os.listdir(d) if f.endswith(".log")
        ]

    if not log_files:
        print("[ERROR] Log File is Not exist")
        return

    for path in log_files:
        print(f"[INFO] Log Monitoring Start: {path}")
        t = threading.Thread(target=process_log_file, args=(path,))
        t.daemon = True
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Log Monitoring Stop. ")

if __name__ == "__main__":
    main()
