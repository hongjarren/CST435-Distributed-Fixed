FROM python:3.11-slim AS builder
WORKDIR /app


COPY proto/ ./proto/
COPY client/requirements.txt ./client/requirements.txt
COPY client/main.py ./client/main.py


RUN pip install --no-cache-dir -r client/requirements.txt


# generate python gRPC code for client
RUN python -m grpc_tools.protoc -I./proto --python_out=./client --grpc_python_out=./client ./proto/compute.proto


FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/client /app
COPY --from=builder /app/proto /app/proto


ENV PYTHONPATH=/app
ENTRYPOINT ["python", "main.py"]