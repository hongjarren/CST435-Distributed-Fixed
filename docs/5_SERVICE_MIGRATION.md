# Migration Guide: 3 Services → 5 Services

This document summarizes the changes made to extend the pipeline from 3 services to 5 services.

---

## What Changed

### Added Services
- **Service D (Processing Fee)**: Adds a 2.5% transaction fee (`int(value * 1.025)`) to the aggregated value
- **Service E (Currency Rounding)**: Rounds the refined value to the nearest $5 (`(value // 5) * 5`)

### New Pipeline Flow
```
Input (5)
  ↓ A: Inventory (+100)
Computed (105)
  ↓ B: Sales tax (×1.15 → int)
Transformed (120)
  ↓ C: Shipping (50 + value//10)
Aggregated (62)
  ↓ D: Processing fee (×1.025 → int)
Refined (63)
  ↓ E: Currency rounding (nearest $5)
Final Result (60)
```

---

## gRPC Changes

### 1. Proto File (`Grpc/proto/compute.proto`)
**Added:**
- `rpc Refine(RefineRequest) returns (RefineResponse);`
- `rpc Finalize(FinalizeRequest) returns (FinalizeResponse);`
- New message types: `RefineRequest`, `RefineResponse`, `FinalizeRequest`, `FinalizeResponse`

### 2. Server (`Grpc/server/main.py`)
**Added methods:**
```python
def Refine(self, request, context):
    result = request.aggregated_value - 5
    return compute_pb2.RefineResponse(result=result, ...)

def Finalize(self, request, context):
    result = request.refined_value // 2
    return compute_pb2.FinalizeResponse(final_result=result, pipeline="A->B->C->D->E", ...)
```

### 3. Client (`Grpc/client/main.py`)
**Updated:**
- `pipeline_call()` now accepts 5 services: `service_a, service_b, service_c, service_d, service_e`
- CSV columns: added `aggregated`, `refined`, `service_d`, `service_e`
- Target parsing: expects 5 comma-separated targets

### 4. Docker Compose (`Grpc/docker-compose.yml`)
**Added services:**
```yaml
serviced:
  environment:
    - SERVICE_NAME=D
  ports:
    - "50064:50051"

servicee:
  environment:
    - SERVICE_NAME=E
  ports:
    - "50065:50051"
```

**Updated client command:**
```yaml
command: ["--targets", "servicea:50051,serviceb:50051,servicec:50051,serviced:50051,servicee:50051", ...]
```

### 5. Distributed Setup (`Grpc/DISTRIBUTED_SETUP.md`)
**Updated:**
- Hardware setup: Now requires 6 laptops (5 services + 1 client)
- IP addresses: Added Laptop 4 (Service D) and Laptop 5 (Service E)
- Expected result: Final result is 60 (was 27)

---

## RMI Changes

### 1. Interface (`RMI/src/main/java/com/cst435/ComputeService.java`)
**Added methods:**
```java
int refine(int aggregatedValue, int workMs) throws RemoteException;
int finalize(int refinedValue, int workMs) throws RemoteException;
```

### 2. Implementation (`RMI/src/main/java/com/cst435/ComputeServiceImpl.java`)
**Added:**
```java
public int refine(int aggregatedValue, int workMs) {
    return aggregatedValue - 5;
}

public int finalize(int refinedValue, int workMs) {
    return refinedValue / 2;
}
```

### 3. Server (`RMI/src/main/java/com/cst435/ComputeServer.java`)
**Updated:**
- Valid SERVICE_NAME now includes `D` and `E`: `[ABCDE]`

### 4. Client (`RMI/src/main/java/com/cst435/LoadTestClient.java`)
**Updated:**
- `TestResult`: Added `aggregated`, `refined`, `serviceD`, `serviceE` fields
- `PipelineWorker`: Accepts 5 hosts, looks up D and E services
- CSV header: `input,computed,transformed,aggregated,refined,final_result,service_a,service_b,service_c,service_d,service_e,send_ts,recv_ts,rtt_ms,error`

### 5. Docker Compose (`RMI/docker-compose.yml`)
**Added services:**
```yaml
serviced:
  environment:
    SERVICE_NAME: D
  ports:
    - "1102:1099"

servicee:
  environment:
    SERVICE_NAME: E
  ports:
    - "1103:1099"
```

**Updated client command:**
```yaml
command: ["--targets", "servicea,serviceb,servicec,serviced,servicee", ...]
```

### 6. Distributed Setup (`RMI/DISTRIBUTED_SETUP.md`)
**Updated:**
- Hardware setup: Now requires 6 laptops
- Firewall rules: Apply to Laptops 1, 2, 3, 4, 5
- Client targets: `--targets "192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13,192.168.1.14"`

---

## Report Outline (`docs/REPORT_OUTLINE.md`)
**Updated:**
- Executive Summary: "5-stage pipeline"
- System Design: "A → B → C → D → E"
- Implementation: Server/client handle A/B/C/D/E
- Figures: Architecture diagram includes all 5 services

---

## New Distributed Client Commands

### gRPC (Python)
```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Docker\Grpc\client

python main.py `
  --targets "192.168.1.10:50051,192.168.1.11:50051,192.168.1.12:50051,192.168.1.13:50051,192.168.1.14:50051" `
  --requests 300 `
  --concurrency 10 `
  --work_ms 10 `
  --input 5 `
  --out C:\Users\<YourUsername>\Desktop\CST435Docker\results\results.csv
```

**Replace IPs** with your actual IPs:
- `192.168.1.10` → Service A
- `192.168.1.11` → Service B
- `192.168.1.12` → Service C
- `192.168.1.13` → Service D
- `192.168.1.14` → Service E

---

### RMI (Java)
```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Docker\RMI

java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient `
  --targets "192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13,192.168.1.14" `
  --requests 300 `
  --concurrency 10 `
  --work_ms 10 `
  --input 5 `
  --out ".\results\results.csv"
```

**Replace IPs** with your actual service IPs (same as gRPC, but without ports).

---

## Testing Changes

### Local (Docker Compose)
```powershell
# gRPC
cd Grpc
docker-compose up --build

# RMI
cd RMI
docker-compose up --build
```

Both now spin up 5 service containers + 1 client container.

### Distributed (6 Laptops)
1. Run Services A, B, C, D, E on Laptops 1–5
2. Run client on your laptop with the commands above
3. Check `results/results.csv` for new columns

---

## Expected Results

### CSV Output
```csv
input,computed,transformed,aggregated,refined,final_result,service_a,service_b,service_c,service_d,service_e,send_ts,recv_ts,rtt_ms,error
5,105,120,62,63,60,192.168.1.10:50051,192.168.1.11:50051,192.168.1.12:50051,192.168.1.13:50051,192.168.1.14:50051,1699999999000,1699999999070,70,
```

### Summary Output
```
=== Experiment Summary ===
Total requests: 300
Total time: ...ms
Average RTT per request: ...ms (expect ~50ms with 10ms work_ms per service)
Min RTT: ...ms
Max RTT: ...ms
```

---

## Lines Changed
- **gRPC**: ~100 lines (proto, server, client, compose, docs)
- **RMI**: ~120 lines (interface, impl, server, client, compose, docs)
- **Total**: ~220 lines across both implementations

---

## Next Steps
1. Test locally with `docker-compose up --build`
2. Deploy to 6 laptops and run distributed test
3. Compare 3-service vs 5-service RTT and throughput
4. Update report with new results and architecture diagrams
