FROM python:3.11-slim AS builder
WORKDIR /app


# install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
python3-dev \
&& rm -rf /var/lib/apt/lists/*


COPY proto/ ./proto/
COPY server/requirements.txt ./server/requirements.txt
COPY server/main.py ./server/main.py


# install python deps
RUN pip install --no-cache-dir -r server/requirements.txt


# generate python gRPC code from proto
RUN python -m grpc_tools.protoc -I./proto --python_out=./server --grpc_python_out=./server ./proto/compute.proto


# --- final image ---
FROM python:3.11-slim
WORKDIR /app


COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/server /app
COPY --from=builder /app/proto /app/proto


ENV PYTHONPATH=/app
EXPOSE 50051


CMD ["python", "main.py"]