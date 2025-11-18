# Distributed Setup Guide - RMI Edition

## 6-Laptop Distributed Experiment (5 Services + Client)

This guide mirrors the gRPC setup but uses **Java RMI** instead of Python/gRPC.

---

## Hardware Setup

- **Laptop 1**: Service A (Java RMI)
- **Laptop 2**: Service B (Java RMI)
- **Laptop 3**: Service C (Java RMI)
- **Laptop 4**: Service D (Java RMI)
- **Laptop 5**: Service E (Java RMI)
- **Your Laptop**: Client (runs load test)

---

## Prerequisites (All Laptops)

1. **Java 11 or higher**
   ```powershell
   java -version
   ```

2. **Maven 3.6+**
   ```powershell
   mvn --version
   ```

3. **Git**
   ```powershell
   git --version
   ```

---

## Step 1: Clone Repository (All Laptops)

```powershell
cd Desktop
git clone https://github.com/hongjarren/CST435Distributed.git
cd CST435Distributed\RMI
```

---

## Step 2: Get IP Addresses (All Laptops)

```powershell
ipconfig
```

Find "IPv4 Address" under your network adapter:
- Laptop 1: `192.168.1.10` (Service A)
- Laptop 2: `192.168.1.11` (Service B)
- Laptop 3: `192.168.1.12` (Service C)
- Laptop 4: `192.168.1.13` (Service D)
- Laptop 5: `192.168.1.14` (Service E)
- Your Laptop: `192.168.1.20` (Client)

**Test connectivity:**
```powershell
ping 192.168.1.10
```

---

## Step 3: Build Locally (All Laptops)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
mvn clean package -DskipTests
```

Output: `target/rmi-distributed-1.0-jar-with-dependencies.jar`

---

## Step 4: Open Firewall Port (Laptops 1, 2, 3, 4, 5)

**PowerShell as Administrator:**

```powershell
New-NetFirewallRule -DisplayName "Allow RMI Port 1099" -Direction Inbound -Protocol TCP -LocalPort 1099 -Action Allow
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Action Allow -Direction Inbound
```

---

## Step 5: Run Services (Laptops 1, 2, 3, 4, 5)

### Laptop 1 (Service A)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
$env:SERVICE_NAME = "A"
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Expected output:**
```
Service A registered as 'ComputeService_A' on port 1099
Waiting for requests...
```

### Laptop 2 (Service B)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
$env:SERVICE_NAME = "B"
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

### Laptop 3 (Service C)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
$env:SERVICE_NAME = "C"
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

### Laptop 4 (Service D)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
$env:SERVICE_NAME = "D"
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

### Laptop 5 (Service E)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
$env:SERVICE_NAME = "E"
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Keep all five terminals open.**

---

## Step 6: Run Client (Your Laptop)

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
New-Item -ItemType Directory -Path ".\results" -Force | Out-Null

java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient `
  --targets "192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13,192.168.1.14" `
  --requests 300 `
  --concurrency 10 `
  --work_ms 10 `
  --input 5 `
  --out ".\results\results.csv"
```

**Replace IPs** with your Service A, B, C, D, E addresses from Step 2.

**Expected output:**
```
RMI Load Test Client
Targets: 192.168.1.10, 192.168.1.11, 192.168.1.12, 192.168.1.13, 192.168.1.14
Requests: 300, Concurrency: 10

=== Experiment Summary ===
Total requests: 300
Total time: ...ms
Average RTT per request: ...ms
Min RTT: ...ms
Max RTT: ...ms
Wrote 300 rows to .\results\results.csv
```

---

## Step 7: Check Results (Your Laptop)

```powershell
Invoke-Item ".\results\results.csv"
```

**Expected columns:**
```
input, computed, transformed, aggregated, refined, final_result, service_a, service_b, service_c, service_d, service_e, send_ts, recv_ts, rtt_ms, error
```

**Example row (input=5):**
```
5,105,120,62,63,60,192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13,192.168.1.14,1763126239680,1763126239750,70,
```

**Calculation trace (business logic pipeline):**
- Input: 5
- After Service A (Inventory: +100): 105
- After Service B (Sales tax: ×1.15): 120
- After Service C (Shipping: + base/10): 62
- After Service D (Processing fee: ×1.025): 63
- After Service E (Currency rounding to $5): 60

---

## Troubleshooting

### "Connection refused"
- Check if services running: `Get-NetTCPConnection -LocalPort 1099`
- Verify IPs: `ipconfig`
- Check firewall: `Get-NetFirewallRule | findstr RMI`

### "Cannot find registry"
- Ensure SERVICE_NAME is set: `$env:SERVICE_NAME = "A"`
- Verify Java is in PATH: `java -version`

### "mvn not found"
- Add Maven to PATH in Windows Environment Variables
- Close and reopen PowerShell
- Run `mvn --version` to verify

---

## Local Testing (Single Machine)

Skip distributed setup and run:

```powershell
cd C:\Users\<YourUsername>\Desktop\CST435Distributed\RMI
docker-compose up --build
```

All services + client run in Docker containers on localhost.

---

## Key Differences from gRPC

| gRPC | RMI |
|------|-----|
| Python-based | Java-based |
| Protocol Buffers | Java objects |
| Port: 50051 | Port: 1099 (RMI registry) |
| Smaller Docker images | Larger Docker images (JVM) |
| Faster serialization | Standard Java serialization |

---

## Next Steps

1. Run local test first: `docker-compose up --build`
2. Deploy to 5 laptops
3. Compare RTT with gRPC version
4. Analyze throughput and latency

Enjoy!
