# RMI Distributed Pipeline - CST 435

A **Java RMI-based** implementation of the same 3-stage distributed pipeline from the gRPC project, but using **Java Remote Method Invocation** instead of protocol buffers.

## Overview

**3-Stage Pipeline:**
- **Service A (Compute)**: Multiplies input by 2
- **Service B (Transform)**: Adds 10 to result
- **Service C (Aggregate)**: Multiplies by 3

**Pipeline Flow**: Input → Service A → Service B → Service C → Final Result

---

## Architecture

### Local Mode (Single Machine)
```
docker-compose up --build
├── servicea (port 1099)
├── serviceb (port 1100 → 1099 internally)
├── servicec (port 1101 → 1099 internally)
└── client (runs 300 load-test requests)
```

### Distributed Mode (5 Physical Laptops)
```
Laptop 1 (Service A): java -cp rmi-distributed.jar com.cst435.ComputeServer
Laptop 2 (Service B): java -cp rmi-distributed.jar com.cst435.ComputeServer
Laptop 3 (Service C): java -cp rmi-distributed.jar com.cst435.ComputeServer
Laptop 5 (Client):    java -cp rmi-distributed.jar com.cst435.LoadTestClient --targets "192.168.1.10,192.168.1.11,192.168.1.12"
```

---

## Project Structure

```
RMI/
├── pom.xml                                  # Maven configuration
├── Dockerfile.server                        # Server container (Java 11)
├── Dockerfile.client                        # Client container
├── docker-compose.yml                       # Local orchestration
├── src/main/java/com/cst435/
│   ├── ComputeService.java                 # Remote interface
│   ├── ComputeServiceImpl.java              # Server implementation
│   ├── ComputeServer.java                  # Server entry point
│   └── LoadTestClient.java                 # Client entry point (load tester)
└── results/                                 # Output CSV (created at runtime)
```

---

## Prerequisites

### For Local Testing
- Java 11+ (OpenJDK recommended)
- Maven 3.6+
- Docker & Docker Compose
- PowerShell (Windows)

### For Distributed Testing
- Java 11+ on all 5 laptops
- Maven 3.6+ on all 5 laptops
- All laptops on same network (WiFi or Ethernet)

---

## Quick Start - Local Mode

```powershell
cd "C:\Users\<YourUsername>\Desktop\Y4 USM\CST 435 Docker\RMI"
docker-compose up --build
```

**Expected output:**
```
rmi-servicea    | Service A registered as 'ComputeService_A' on port 1099
rmi-serviceb    | Service B registered as 'ComputeService_B' on port 1099
rmi-servicec    | Service C registered as 'ComputeService_C' on port 1099
rmi-client      | === Experiment Summary ===
rmi-client      | Total requests: 300
rmi-client      | Total time: 3245ms (3.25s)
rmi-client      | Wrote 300 rows to /app/results/results.csv
```

**Check results:**
```powershell
Invoke-Item ".\results\results.csv"
```

---

## Distributed Setup (5 Laptops)

### Step 1: Prepare All Laptops

On each laptop:

```powershell
# Install Java 11
# Download from: https://adoptopenjdk.net/ or use Windows Store

# Verify
java -version

# Install Maven
# Download from: https://maven.apache.org/download.cgi
# Add to PATH (Windows: setx PATH "%PATH%;C:\Program Files\Apache\maven\bin")

# Verify
mvn --version
```

### Step 2: Clone Repository

On each laptop:

```powershell
cd Desktop
git clone https://github.com/hongjarren/CST435Distributed.git
cd CST435Distributed\RMI
```

### Step 3: Compile Locally

On each laptop:

```powershell
mvn clean package -DskipTests
```

Creates: `target/rmi-distributed-1.0-jar-with-dependencies.jar`

### Step 4: Get IP Addresses

On each laptop, run:

```powershell
ipconfig
```

Record the IPv4 addresses:
- Laptop 1 (Service A): `192.168.1.10`
- Laptop 2 (Service B): `192.168.1.11`
- Laptop 3 (Service C): `192.168.1.12`

### Step 5: Start Services (Laptops 1, 2, 3)

**Laptop 1 (Service A):**
```powershell
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar -DSERVICE_NAME=A com.cst435.ComputeServer
```

**Laptop 2 (Service B):**
```powershell
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar -DSERVICE_NAME=B com.cst435.ComputeServer
```

**Laptop 3 (Service C):**
```powershell
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar -DSERVICE_NAME=C com.cst435.ComputeServer
```

**Keep these terminals open.**

### Step 6: Run Client (Laptop 5)

```powershell
java -cp target/rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient `
  --targets "192.168.1.10,192.168.1.11,192.168.1.12" `
  --requests 300 `
  --concurrency 10 `
  --work_ms 10 `
  --input 5 `
  --out ".\results\results.csv"
```

**Replace IPs** with your actual Service A, B, C addresses.

### Step 7: Check Results

```powershell
Invoke-Item ".\results\results.csv"
```

---

## Command-Line Arguments

### Server
```
SERVICE_NAME=A|B|C   # Which service to run (environment variable)
PORT=1099            # RMI registry port (default 1099)
```

### Client
```
--targets <host1,host2,host3>    # Comma-separated hostnames or IPs for A,B,C
--requests <N>                   # Total requests (default 300)
--concurrency <N>                # Parallel threads (default 10)
--work_ms <N>                    # Simulated work per service in ms (default 10)
--input <N>                      # Input value (default 5)
--out <path>                     # Output CSV file (default ./results/results.csv)
```

**Example:**
```powershell
java -cp rmi-distributed.jar com.cst435.LoadTestClient `
  --targets "serviceA.local,serviceB.local,serviceC.local" `
  --requests 1000 `
  --concurrency 20 `
  --work_ms 5 `
  --input 42 `
  --out "C:\Users\hongj\Desktop\results.csv"
```

---

## Output Format

**CSV Columns:**
```
input, computed, transformed, final_result, service_a, service_b, service_c, send_ts, recv_ts, rtt_ms, error
```

**Example Row (input=5):**
```
5,10,20,60,servicea,serviceb,servicec,1763126239680,1763126239686,6,
```

**Calculation:**
- Input: 5
- After Service A: 5 × 2 = 10
- After Service B: 10 + 10 = 20
- After Service C: 20 × 3 = 60
- RTT: 6ms

---

## Firewall Rules

### Windows Firewall (Distributed Mode)

On each service laptop, enable RMI port (1099):

**PowerShell (Admin):**
```powershell
New-NetFirewallRule -DisplayName "Allow RMI Port 1099" -Direction Inbound -Protocol TCP -LocalPort 1099 -Action Allow
```

Also enable ping (ICMP):
```powershell
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Action Allow -Direction Inbound
```

---

## Troubleshooting

### "Connection refused" on client
- Verify services are running: `netstat -an | findstr 1099`
- Check firewall: `Get-NetFirewallRule | Where {$_.DisplayName -match "RMI"}`
- Verify IP addresses: `ipconfig`
- Test connectivity: `ping 192.168.1.10`

### "Service not bound in registry"
- Ensure correct SERVICE_NAME environment variable: `$env:SERVICE_NAME = "A"`
- Check RMI registry is running: `jps` (should show rmiregistry)
- Restart the service

### "Cannot compile: mvn not found"
- Add Maven to PATH: `setx PATH "%PATH%;C:\Program Files\Apache\maven\bin"`
- Close and reopen PowerShell
- Run `mvn --version` to verify

### Slow RTT on distributed
- Check network latency: `ping -n 1 <service-ip>`
- Increase `--work_ms` if services are overloaded
- Run `--concurrency 1` to test with single request

---

## Comparison: gRPC vs RMI

| Feature | gRPC | RMI |
|---------|------|-----|
| Language | Language-agnostic (Python example) | Java-only |
| Serialization | Protocol Buffers | Java serialization |
| Transport | HTTP/2 | TCP/custom |
| Performance | Very fast, low overhead | Slightly slower (serialization) |
| Learning Curve | Moderate (protobuf syntax) | Easy (standard Java) |
| Docker Size | Smaller | Larger (JVM) |

---

## Next Steps

1. Run local test: `docker-compose up --build`
2. Compare results with gRPC version
3. Deploy to 5 laptops for distributed testing
4. Analyze RTT measurements and throughput

---

## Questions?

Refer to the gRPC version in `../proto/` for comparison, or check the source code comments in `src/main/java/com/cst435/`.
