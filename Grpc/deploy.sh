#!/usr/bin/env bash


# Usage: ./deploy.sh <host-ip> <image> <service-name> [port]
# Example: ./deploy.sh 10.0.0.11 demo/compute:1.0 A 50051


HOST=$1
IMAGE=$2
SERVICE_NAME=$3
PORT=${4:-50051}


if [ -z "$HOST" ] || [ -z "$IMAGE" ] || [ -z "$SERVICE_NAME" ]; then
echo "Usage: $0 <host-ip> <image> <service-name> [port]"
exit 1
fi


# This script assumes passwordless SSH or will prompt for password.
# It pulls the image and runs the container on the remote host.


ssh $HOST "docker pull $IMAGE && docker stop compute_$SERVICE_NAME || true && docker rm compute_$SERVICE_NAME || true && docker run -d --name compute_$SERVICE_NAME -e SERVICE_NAME=$SERVICE_NAME -p $PORT:50051 --restart unless-stopped $IMAGE"


if [ $? -eq 0 ]; then
echo "Deployed $SERVICE_NAME to $HOST"
else
echo "Failed to deploy to $HOST"
fi