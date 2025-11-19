# HTTP/REST Distributed Computing Pipeline

Use the commands below to build the containers, run them locally or across multiple machines, and execute the client load test. 

## Quick PowerShell Commands

### Experiment: Distributed Computing on Separate Machines
## Local Testing (Single Machine)

### Step 1: Build and Start Services

```bash
cd http-rest
docker-compose -f docker-compose-pipeline.yml up --build
```

This starts the entire pipeline:
- Service A → http://localhost:5000
- Service B → http://localhost:5001
- Service C → http://localhost:5002
- Service D → http://localhost:5003
- Service E → http://localhost:5004

### Step 2: Run the Client

In a separate terminal:

```bash
cd http-rest
python client/client.py --targets "http://localhost:5000,http://localhost:5001,http://localhost:5002,http://localhost:5003,http://localhost:5004" --requests 300 --concurrency 10 --work_ms 10 --input 5
```

### Step 3: View Results

- CSV written to `http-rest/results/results.csv`
- Columns: `input, computed, transformed, aggregated, refined, final_result, service_a, service_b, service_c, service_d, service_e, send_ts, recv_ts, rtt_ms, error`
- Example row (input 5):
  ```
  5,105,120,62,63,60,http://...5000,http://...5001,http://...5002,http://...5003,http://...5004,1763...,1763...,64,
  ```

## Distributed Deployment (Multiple Machines)

### Prerequisites

- 6 physical machines on the same network (5 services + 1 client)
- Docker installed on each service machine
- Port 5000 open on service laptops

### Step 1: Collect IPs

Run `ipconfig` (Windows) or `ifconfig`/`ip addr` (Linux/macOS) on each machine and record IPv4 addresses.

### Step 2: Open Firewall Ports (Service Laptops 1-5)

```powershell
New-NetFirewallRule -DisplayName "Allow HTTP Pipeline" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Step 3: Build Docker Images (per laptop)

| Laptop | Service | Commands |
|--------|---------|----------|
| 1 | Service A | `cd http-rest/service_a && docker build -t cst435docker-servicea .` |
| 2 | Service B | `cd http-rest/service_b && docker build -t cst435docker-serviceb .` |
| 3 | Service C | `cd http-rest/service_c && docker build -t cst435docker-servicec .` |
| 4 | Service D | `cd http-rest/service_d && docker build -t cst435docker-serviced .` |
| 5 | Service E | `cd http-rest/service_e && docker build -t cst435docker-servicee .` |

### Step 4: Run Each Service

All services expose port 5000 on their host:

```bash
# Laptop 1
docker run -it --rm `
    -e SERVICE_NAME=A `
    -e WORK_MS=10 `
    -e BASE_STOCK=100 `
    -e PORT=5000 `
    -p 5000:5000 `
    cst435distributed-servicea
# Laptop 2
docker run -it --rm `
    -e SERVICE_NAME=B `
    -e WORK_MS=10 `
    -e BASE_STOCK=100 `
    -e PORT=5000 `
    -p 5000:5000 `
    cst435distributed-serviceb

# Laptop 3
docker run -it --rm `
    -e SERVICE_NAME=C `
    -e WORK_MS=10 `
    -e BASE_STOCK=100 `
    -e PORT=5000 `
    -p 5000:5000 `
    cst435distributed-servicec

# Laptop 4
docker run -it --rm `
    -e SERVICE_NAME=D `
    -e WORK_MS=10 `
    -e BASE_STOCK=100 `
    -e PORT=5000 `
    -p 5000:5000 `
    cst435distributed-serviced

# Laptop 5
docker run -it --rm `
    -e SERVICE_NAME=E `
    -e WORK_MS=10 `
    -e BASE_STOCK=100 `
    -e PORT=5000 `
    -p 5000:5000 `
    cst435distributed-servicee
```

### Step 5: Run Client (Laptop 6)

```bash
cd http-rest/client
pip install -r requirements.txt

python client.py \
  --targets "http://192.168.1.10:5000,http://192.168.1.11:5000,http://192.168.1.12:5000,http://192.168.1.13:5000,http://192.168.1.14:5000" \
  --requests 300 \
  --concurrency 10 \
  --work_ms 10 \
  --input 5
```

Replace IPs with your real addresses (A→E order).

## API Endpoints

Every service exposes:

- `POST /process`  
  Request:
  ```json
  { "value": 105 }
  ```
  Response:
  ```json
  { "value": 120, "service": "B", "status": "success" }
  ```

- `GET /health`  
  Response:
  ```json
  { "status": "healthy", "service": "service-C", "operation": "shipping cost", "timestamp": 1763126239.68 }
  ```

## Configuration

### Environment Variables

| Service | Variables | Meaning (default) |
|---------|-----------|-------------------|
| A | `BASE_STOCK` | Base inventory added to input (100) |
| B | `TAX_RATE` | Sales tax percentage (0.15) |
| C | `BASE_SHIPPING`, `UNIT_DIVISOR` | Base cost (50) + value/10 |
| D | `FEE_RATE` | Processing fee percentage (0.025) |
| E | `ROUND_BASE` | Rounding bucket (5) |
| All | `SERVICE_NAME`, `PORT`, `WORK_MS` | Standard metadata/port/delay |

### Client Arguments

- `--targets`: Comma-separated URLs for Services A-E (required)
- `--requests`: Total requests (default 300)
- `--concurrency`: Parallel requests (default 10)
- `--work_ms`: Work simulation hint (default 10, informational)
- `--input`: Input value per request (default 5)
- `--output`: CSV filename (default `results.csv`)

## Expected Results (Input = 5)

| Stage | Service | Output |
|-------|---------|--------|
| 1 | Service A (Inventory +100) | 105 |
| 2 | Service B (Sales Tax) | 120 |
| 3 | Service C (Shipping) | 62 |
| 4 | Service D (Processing Fee) | 63 |
| 5 | Service E (Currency Rounding) | **60** |

Performance snapshot (local Docker, 10 concurrency, 10ms work/service):
```
=== Experiment Summary ===
Total requests: 300
Successful requests: 300
Failed requests: 0
Total time: ~3.2 seconds
Average RTT per request: 60±5 ms
Throughput: ~90-95 requests/second
```

## Testing Individual Services

```bash
# Service A
curl -X POST http://localhost:5000/process -H "Content-Type: application/json" -d '{"value": 5}'

# Service B
curl -X POST http://localhost:5001/process -H "Content-Type: application/json" -d '{"value": 105}'

# Service C
curl -X POST http://localhost:5002/process -H "Content-Type: application/json" -d '{"value": 120}'

# Service D
curl -X POST http://localhost:5003/process -H "Content-Type: application/json" -d '{"value": 62}'

# Service E
curl -X POST http://localhost:5004/process -H "Content-Type: application/json" -d '{"value": 63}'
```
