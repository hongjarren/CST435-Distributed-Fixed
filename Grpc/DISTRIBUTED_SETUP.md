# Distributed gRPC Pipeline Setup Guide

## Overview
This project implements a **5-stage gRPC pipeline** across multiple physical laptops:
- **Service A (Compute)**: Multiplies input by 2
- **Service B (Transform)**: Adds 10 to result
- **Service C (Aggregate)**: Multiplies by 3
- **Service D (Refine)**: Subtracts 5 from result
- **Service E (Finalize)**: Divides by 2 for final result

**Pipeline Flow**: Input → Service A → Service B → Service C → Service D → Service E → Final Result

---

## Hardware Setup
- **Laptop 1**: Service A (Docker container)
- **Laptop 2**: Service B (Docker container)
- **Laptop 3**: Service C (Docker container)
- **Laptop 4**: Service D (Docker container)
- **Laptop 5**: Service E (Docker container)
- **Your Laptop**: Client (runs load test, generates results.csv)

All laptops must be on the **same network** and able to ping each other.

---

## Prerequisites (All Laptops)

### 1. Install Python 3.11
- Download from [python.org](https://www.python.org/downloads/) or Microsoft Store
- Verify: `python --version` (should be 3.11.x)

### 2. Install Docker Desktop
- Download from [docker.com](https://www.docker.com/products/docker-desktop)
- Start Docker Desktop
- Verify: `docker --version`

### 3. Install Git
- Download from [git-scm.com](https://git-scm.com/download/win)
- Verify: `git --version`

---

## Step 1: Get the Code (All Laptops)

Clone the repository on all 5 laptops:

```powershell
cd Desktop
git clone <your-repo-url>
cd CST435Docker
```

Each laptop now has these files:
```
CST435Docker/
├── proto/
│   └── compute.proto
├── server/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── client/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── docker-compose.yml
```

---

## Step 2: Get IP Addresses (All Laptops)

Open PowerShell and run:
```powershell
ipconfig
```

Look for "IPv4 Address" under your network adapter. Example:
- Laptop 1 (Service A): `192.168.1.10`
- Laptop 2 (Service B): `192.168.1.11`
- Laptop 3 (Service C): `192.168.1.12`
- Laptop 4 (Service D): `192.168.1.13`
- Laptop 5 (Service E): `192.168.1.14`
- Your Laptop (Client): `192.168.1.20`

**Write these down!** You'll need them in Step 4.

Test connectivity:
```powershell
ping 192.168.1.10
```

---

## Step 3: Build Docker Images (All Laptops)

On **each of laptops 1, 2, 3, 4, 5, and your client laptop**, build the images:

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Docker
docker-compose build
```

This creates images for all services including:
- `cst435docker-servicea`
- `cst435docker-serviceb`
- `cst435docker-servicec`
- `cst435docker-serviced`
- `cst435docker-servicee`
- `cst435docker-client`

Each laptop has all images, but will only run one service.

---

## Step 4: Run Services (Laptops 1, 2, 3, 4, 5)

### Laptop 1 (Service A)
```powershell
docker run -e SERVICE_NAME=A -e PORT=50051 -p 50051:50051 --rm cst435docker-servicea
```
**Output:** You should see:
```
A starting on 0.0.0.0:50051
```

### Laptop 2 (Service B)
```powershell
docker run -e SERVICE_NAME=B -e PORT=50051 -p 50051:50051 --rm cst435docker-serviceb
```
**Output:**
```
B starting on 0.0.0.0:50051
```

### Laptop 3 (Service C)
```powershell
docker run -e SERVICE_NAME=C -e PORT=50051 -p 50051:50051 --rm cst435docker-servicec
```
**Output:**
```
C starting on 0.0.0.0:50051
```

### Laptop 4 (Service D)
```powershell
docker run -e SERVICE_NAME=D -e PORT=50051 -p 50051:50051 --rm cst435docker-serviced
```
**Output:**
```
D starting on 0.0.0.0:50051
```

### Laptop 5 (Service E)
```powershell
docker run -e SERVICE_NAME=E -e PORT=50051 -p 50051:50051 --rm cst435docker-servicee
```
**Output:**
```
E starting on 0.0.0.0:50051
```

**Keep these terminals open** — the services must be running for the client to work.

---

## Step 5: Run Client (Your Laptop)

On **your laptop**, open a new PowerShell and run:

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Docker\client

python main.py `
  --targets "192.168.1.10:50051,192.168.1.11:50051,192.168.1.12:50051,192.168.1.13:50051,192.168.1.14:50051" `
  --requests 300 `
  --concurrency 10 `
  --work_ms 10 `
  --input 5 `
  --out C:\Users\<YourUsername>\Desktop\CST435Docker\results\results.csv
```

**Replace the IP addresses** with the actual IPs from Step 2.
**Format**: `service_a_ip:port,service_b_ip:port,service_c_ip:port,service_d_ip:port,service_e_ip:port`

**Expected output:**
```
=== Experiment Summary ===
Total requests: 300
Total time: ...ms
Average RTT per request: ...ms
Min RTT: ...ms
Max RTT: ...ms
Wrote 300 rows to C:\Users\<YourUsername>\Desktop\CST435Docker\results\results.csv
```

---

## Step 6: Check Results (Your Laptop)

Open the results file:
```powershell
Invoke-Item C:\Users\<YourUsername>\Desktop\CST435Docker\results\results.csv
```

**Expected CSV columns:**
```
input, computed, transformed, aggregated, refined, final_result, service_a, service_b, service_c, service_d, service_e, send_ts, recv_ts, rtt_ms, error
```

**Example row (input=5):**
```
5, 10, 20, 60, 55, 27, 192.168.1.10:50051, 192.168.1.11:50051, 192.168.1.12:50051, 192.168.1.13:50051, 192.168.1.14:50051, ..., ..., 250, 
```

**Calculation trace:**
- Input: 5
- After Service A (×2): 5 × 2 = 10
- After Service B (+10): 10 + 10 = 20
- After Service C (×3): 20 × 3 = 60
- After Service D (-5): 60 - 5 = 55
- After Service E (÷2): 55 ÷ 2 = 27
- Final Result: 27

---

## File Structure Summary

### Each Laptop Needs:
```
Desktop/CST435Docker/
├── proto/compute.proto          (same for all)
├── server/Dockerfile            (same for all)
├── server/main.py               (same for all)
├── server/requirements.txt       (same for all)
├── client/Dockerfile            (same for all)
├── client/main.py               (same for all)
├── client/requirements.txt       (same for all)
└── docker-compose.yml           (same for all)
```

### Only Laptop 5 Needs:
```
Desktop/CST435Docker/results/    (folder, can be empty initially)
```

---

## Comparison: Local vs Distributed

### Local (Single Laptop)
```
docker-compose up --build
# Client calls: servicea:50051,serviceb:50051,servicec:50051,serviced:50051,servicee:50051 (Docker DNS)
```

### Distributed (6 Laptops - What You're Doing Now)
```
# Laptop 1: docker run ... cst435docker-servicea
# Laptop 2: docker run ... cst435docker-serviceb
# Laptop 3: docker run ... cst435docker-servicec
# Laptop 4: docker run ... cst435docker-serviced
# Laptop 5: docker run ... cst435docker-servicee
# Your Laptop: python client/main.py --targets "192.168.1.10:50051,..."
# Client calls: Real IP addresses for all 5 services
```

---

## Troubleshooting

### "Connection refused" error
- Check if services are running: `docker ps`
- Verify IP addresses are correct: `ipconfig`
- Ping the other laptops: `ping 192.168.1.10`
- Ensure firewall allows port 50051

### "Host is unreachable"
- Laptops are not on the same network
- Check WiFi/Ethernet connection
- Try connecting to network switch instead of WiFi

### Service doesn't start
- Make sure you built images: `docker-compose build`
- Check Docker is running: `docker ps`

### Client gets "timeout"
- Services might be too slow
- Increase timeout: Add `--timeout 30` to client command
- Or increase `--work_ms` to simulate faster processing

---

## Example Full Experiment

**Setup:**
- Requests: 300 (total calls through the pipeline)
- Concurrency: 10 (10 parallel requests)
- Work time: 10ms per service (5 services = 50ms total per request)
- Input value: 5

**Expected Results in CSV:**
- 300 rows of results
- RTT (round-trip time) ≈ 50ms + network latency
- All final_result values should be 27 (because input=5 → 10 → 20 → 60 → 55 → 27)
- Some errors may occur due to network issues

---

## Questions?
Ask your teammates or refer back to this guide!
