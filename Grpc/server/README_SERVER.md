Server usage notes:
- environment variables supported:
- SERVICE_NAME (e.g. A,B,C)
- PORT (defaults to 50051)


Example run (locally):
docker build -t demo/compute:1.0 .
docker run -e SERVICE_NAME=A -p 50051:50051 demo/compute:1.0