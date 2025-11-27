# RMI Distributed Test - Complete Step-by-Step Guide

## Prerequisites (All 6 Laptops)

1. Java 11+ installed
2. Maven 3.6+ installed
3. All laptops on same WiFi network
4. Git installed

---

## Part 1: Setup (Do Once on All Laptops)

### On ALL 6 Laptops (5 servers + 1 client)

**Step 1.1: Clone Repository**
```powershell
cd Desktop
git clone https://github.com/hongjarren/CST435-Distributed-Fixed.git
cd "CST435-Distributed-Fixed\RMI"
```

**Step 1.2: Build JAR File**
```powershell
mvn clean package -DskipTests
```
Wait for "BUILD SUCCESS" message. This creates `target\rmi-distributed-1.0-jar-with-dependencies.jar`

**Step 1.3: Get IP Address**
```powershell
ipconfig
```
Look for "IPv4 Address" - write it down for each laptop:
- Laptop 1: `_________________` (will run Service A)
- Laptop 2: `_________________` (will run Service B)
- Laptop 3: `_________________` (will run Service C)
- Laptop 4: `_________________` (will run Service D)
- Laptop 5: `_________________` (will run Service E)
- Laptop 6: `_________________` (your client laptop)

**Step 1.4: Open Firewall (Server Laptops 1-5 Only)**

Run PowerShell **as Administrator** on laptops 1, 2, 3, 4, 5:
```powershell
New-NetFirewallRule -DisplayName "Allow RMI Port 1099" -Direction Inbound -Protocol TCP -LocalPort 1099 -Action Allow
```

---

## Part 2: Start Services (Laptops 1-5)

Keep each terminal window open - don't close them!

### Laptop 1 - Run Service A

```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "A"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_LAPTOP1_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Replace `YOUR_LAPTOP1_IP`** with Laptop 1's actual IP address.

**Expected output:**
```
Service A registered as 'ComputeService_A' on port 1099
Waiting for requests...
```

✅ **Service A is ready!** Leave this window open.

---

### Laptop 2 - Run Service B

```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "B"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_LAPTOP2_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Expected output:**
```
Service B registered as 'ComputeService_B' on port 1099
Waiting for requests...
```

✅ **Service B is ready!** Leave this window open.

---

### Laptop 3 - Run Service C

```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "C"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_LAPTOP3_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Expected output:**
```
Service C registered as 'ComputeService_C' on port 1099
Waiting for requests...
```

✅ **Service C is ready!** Leave this window open.

---

### Laptop 4 - Run Service D

```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "D"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_LAPTOP4_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Expected output:**
```
Service D registered as 'ComputeService_D' on port 1099
Waiting for requests...
```

✅ **Service D is ready!** Leave this window open.

---

### Laptop 5 - Run Service E

```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "E"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_LAPTOP5_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

**Expected output:**
```
Service E registered as 'ComputeService_E' on port 1099
Waiting for requests...
```

✅ **Service E is ready!** Leave this window open.

---

## Part 3: Run Client (Laptop 6)

### On Client Laptop

**Step 3.1: Verify Connectivity (Optional but Recommended)**

Test connection to all 5 services:
```powershell
Test-NetConnection -ComputerName LAPTOP1_IP -Port 1099
Test-NetConnection -ComputerName LAPTOP2_IP -Port 1099
Test-NetConnection -ComputerName LAPTOP3_IP -Port 1099
Test-NetConnection -ComputerName LAPTOP4_IP -Port 1099
Test-NetConnection -ComputerName LAPTOP5_IP -Port 1099
```

Look for `TcpTestSucceeded : True` in each response.

**Step 3.2: Create Results Directory**
```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
New-Item -ItemType Directory -Force -Path ".\results"
```

**Step 3.3: Run Load Test Client**

```powershell
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient --targets "LAPTOP1_IP,LAPTOP2_IP,LAPTOP3_IP,LAPTOP4_IP,LAPTOP5_IP" --requests 300 --concurrency 10 --work_ms 10 --input 5 --out ".\results\results.csv"
```

**Replace the IPs** with your actual laptop IP addresses in order (A, B, C, D, E).

**Example with real IPs:**
```powershell
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient --targets "192.168.43.159,192.168.43.37,192.168.43.155,192.168.43.211,192.168.43.160" --requests 300 --concurrency 10 --work_ms 10 --input 5 --out ".\results\results.csv"
```

**Expected output:**
```
=== Experiment Summary ===
Total requests: 300
Successful requests: 300
Failed requests: 0
Total time: 5.23 seconds (5230ms)
Average RTT per request: 174.33ms
Min RTT: 150ms
Max RTT: 250ms
Throughput: 57.36 requests/second

Results saved to: .\results\results.csv
```

**Step 3.4: View Results**
```powershell
Invoke-Item ".\results\results.csv"
```

---

## Part 4: What You Should See

### On Server Laptops (1-5)

Each service terminal should show logs like:
```
[Service A] compute(5) = 105
[Service A] compute(5) = 105
[Service A] compute(5) = 105
...
```

### On Client Laptop (6)

- Summary statistics printed to console
- CSV file created in `.\results\results.csv`
- 300 rows of data with columns: input, computed, transformed, aggregated, refined, final_result, timestamps, RTT, etc.

---

## Example Pipeline Flow (input=5)

```
Input: 5
   ↓
Service A (Inventory: +100)        → 105
   ↓
Service B (Sales Tax: ×1.15)       → 120
   ↓
Service C (Shipping: 50 + val/10)  → 62
   ↓
Service D (Processing: ×1.025)     → 63
   ↓
Service E (Rounding to $5)         → 60
   ↓
Final Result: 60
```

---

## Troubleshooting

### Problem: "Connection refused" or "cannot find registry"

**Solution:** On server laptops, stop the service (Ctrl+C) and restart with explicit hostname:
```powershell
$env:SERVICE_NAME = "A"
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=192.168.43.159"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```
Replace IP with the actual server's IP.

### Problem: "No response from services"

**Check:**
1. All 5 services are running (check each terminal)
2. Firewall rule added on server laptops
3. Test-NetConnection succeeds from client to all servers
4. IPs in --targets match the actual server IPs

### Problem: "Target file does not exist"

**Solution:** Run `mvn clean package -DskipTests` again on that laptop.

### Problem: Client just hangs

**Solution:** 
- Press Ctrl+C to stop
- Reduce test size: `--requests 10 --concurrency 1`
- Check if ANY service responded in the CSV file

---

## Quick Reference Commands

### Start Server (any of laptops 1-5)
```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
$env:SERVICE_NAME = "A"  # Change to B, C, D, or E
$env:JAVA_OPTS = "-Djava.rmi.server.hostname=YOUR_IP"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.ComputeServer
```

### Start Client (laptop 6)
```powershell
cd "Desktop\CST435-Distributed-Fixed\RMI"
java -cp target\rmi-distributed-1.0-jar-with-dependencies.jar com.cst435.LoadTestClient --targets "IP_A,IP_B,IP_C,IP_D,IP_E" --requests 300 --concurrency 10 --work_ms 10 --input 5 --out ".\results\results.csv"
```

### Stop Everything
Press **Ctrl+C** in each terminal window.

---

## Summary Checklist

- [ ] All 6 laptops have code cloned
- [ ] All 6 laptops have JAR built (`mvn clean package`)
- [ ] IP addresses written down for all 6 laptops
- [ ] Firewall rules added on server laptops 1-5
- [ ] Service A running on Laptop 1
- [ ] Service B running on Laptop 2
- [ ] Service C running on Laptop 3
- [ ] Service D running on Laptop 4
- [ ] Service E running on Laptop 5
- [ ] Client command run on Laptop 6
- [ ] Results CSV file created and verified

---

**Good luck with your distributed RMI experiment!**
