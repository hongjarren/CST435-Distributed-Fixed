# gRPC (Python) — 5-Stage Business Pipeline

This folder contains a Python gRPC implementation of a 5-stage pipeline that performs simple but realistic business operations:

- Service A — Inventory: value + 100
- Service B — Sales tax: int(value × 1.15)
- Service C — Shipping: 50 + (value // 10)
- Service D — Processing fee: int(value × 1.025)
- Service E — Currency rounding: (value // 5) × 5

Example (input=5) flows as 5 → 105 → 120 → 62 → 63 → 60 (final result).

## Quick Start (Local, Docker Compose)

Build and run all five services plus the client on one machine:

```powershell
cd "C:\Users\<you>\...\CST 435 Docker\Grpc"
docker-compose up --build
```

What you’ll see:
- Client prints an experiment summary (total requests, total time, avg/min/max RTT)
- CSV results at `Grpc/results/results.csv`

Default compose client command executes:
- `--targets servicea:50051,serviceb:50051,servicec:50051,serviced:50051,servicee:50051`
- `--requests 300 --concurrency 10 --work_ms 10 --input 5`

## Distributed Run (Multiple Machines)

Build the server image on each service machine once:

```powershell
cd "C:\Users\<you>\...\CST 435 Docker\Grpc"
docker build -f server/Dockerfile -t grpc-server:latest .
```

Start one service container per machine (replace X with A/B/C/D/E):

```powershell
docker run --rm -e SERVICE_NAME=X -p 50051:50051 grpc-server:latest
```

Tip (Windows firewall):

```powershell
New-NetFirewallRule -DisplayName "gRPC 50051" -Direction Inbound -LocalPort 50051 -Protocol TCP -Action Allow
```

Run the client on a separate machine (two options):

Option A — Python locally:
```powershell
cd "C:\Users\<you>\...\CST 435 Docker\Grpc\client"
pip install -r requirements.txt
python main.py --targets "IP_A:50051,IP_B:50051,IP_C:50051,IP_D:50051,IP_E:50051" --requests 300 --concurrency 10 --work_ms 10 --input 5 --out ".\results\results.csv"
```

Option B — Docker client container:
```powershell
cd "C:\Users\<you>\...\CST 435 Docker\Grpc"
docker build -f client/Dockerfile -t grpc-client:latest .
mkdir results
docker run --rm -v ${PWD}\results:/tmp grpc-client:latest --targets "IP_A:50051,IP_B:50051,IP_C:50051,IP_D:50051,IP_E:50051" --requests 300 --concurrency 10 --work_ms 10 --input 5 --out "/tmp/results.csv"
```

## Parameters
- `--targets`: comma list of five endpoints in order A,B,C,D,E
- `--requests`: total requests to perform
- `--concurrency`: parallel workers used by the client
- `--work_ms`: per-service artificial work (sleep) to simulate load
- `--input`: starting value supplied to Service A
- `--out`: path to CSV output

## Expected Output
Sample first row for input=5:

```
input,computed,transformed,aggregated,refined,final_result,...
5,105,120,62,63,60,...
```

## Troubleshooting
- Connectivity: from client, `Test-NetConnection -ComputerName IP_A -Port 50051`
- Firewall: ensure inbound TCP/50051 allowed on service hosts
- Timeouts: if you see deadline exceeded, reduce `concurrency` or increase timeouts
- Verifying: check container logs, and inspect `results/results.csv`