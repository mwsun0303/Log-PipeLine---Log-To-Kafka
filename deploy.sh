DOCKER_FILE="Dockerfile"
CONTAINER_NAME="log_to_kafka"
IMAGE_NAME="${CONTAINER_NAME}_image"

# Mount Path는 모니터링 로그의 상위 경로로 설정, 설정한 경로 내 모든 .log 파일 모니터링
MOUNT_PATH="[Log Path]"         

echo "[INFO] -------------------------- "
echo "[INFO] Old Container Remove "
echo "[INFO] -------------------------- "
    docker ps -a --filter "ancestor=$IMAGE_NAME" --format "{{.ID}}" | xargs -r docker rm -f
    echo "[INFO] Old Container Remove Check"
        docker ps -a

echo "[INFO] -------------------------- "
echo "[INFO] Log Forward API Build Start "
echo "[INFO] -------------------------- "
    docker build -t $IMAGE_NAME -f $DOCKER_FILE .

echo "[INFO] -------------------------- "
echo "[INFO] Log Forward API Docker Container Run "
echo "[INFO] -------------------------- "
    CONTAINER_ID=$(docker run -d -v $MOUNT_PATH:$MOUNT_PATH --name $CONTAINER_NAME $IMAGE_NAME)
    echo "[INFO] Container started with ID: $CONTAINER_ID"

echo "[INFO] -------------------------- "
echo "[INFO] Container Log 10sec"
echo "[INFO] -------------------------- "
    timeout 10 docker logs -f $CONTAINER_ID

echo "[INFO] -------------------------- "
echo "[INFO] Deploy Success"
echo "[INFO] -------------------------- "