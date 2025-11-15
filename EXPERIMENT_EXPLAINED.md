# Distributed Systems Experiment: Complete Guide

## What Are We Doing?

We're building a **distributed computing system** that mimics real-world scenarios where:
- **Multiple computers** work together over a network
- **Each computer handles one task** in a pipeline
- **Tasks are processed sequentially** (output of one feeds into the next)
- **We measure performance** (speed, latency, throughput)

Think of it like an assembly line in a factory:
- **Station A** (Computer 1): Does operation 1
- **Station B** (Computer 2): Does operation 2 on the output of A
- **Station C** (Computer 3): Does operation 3 on the output of B
- **Inspector** (Your Laptop): Sends items down the line and records results

---

## The Experiment Overview

### Goal
Send **300 requests** through a 3-stage pipeline running on **3 separate physical computers** and measure how long each request takes.

### The Pipeline (What Each Computer Does)

```
Input (5)
   ↓
[Laptop 1 - Service A]  → Multiply by 2    → (5 × 2 = 10)
   ↓
[Laptop 2 - Service B]  → Add 10          → (10 + 10 = 20)
   ↓
[Laptop 3 - Service C]  → Multiply by 3   → (20 × 3 = 60)
   ↓
Result: 60
```

Every request goes through this exact sequence on three different machines.

---

## Hardware Setup

You need **5 physical laptops**:

| Laptop | Role | Responsibility |
|--------|------|-----------------|
| **1** | Service A | Multiply numbers by 2 |
| **2** | Service B | Add 10 to numbers |
| **3** | Service C | Multiply numbers by 3 |
| **4** | Spare | Not used in this experiment |
| **5** | Client | Send 300 requests & record results |

All 5 laptops must be connected to the **same network** (WiFi or Ethernet).

---

## Two Implementations: gRPC vs RMI

We have two versions of the same experiment:

### Version 1: gRPC (Python-based)
```
Server: Python 3.11
Client: Python 3.11
Communication: Protocol Buffers over HTTP/2
Folder: /proto (proto file definition)
```

### Version 2: RMI (Java-based)
```
Server: Java 11
Client: Java 11
Communication: Java Remote Method Invocation
Folder: /RMI (Java source code)
```

**Both do the same thing — just different languages and technologies.**

---

## How It Works: Step-by-Step

### Step 1: Each Laptop Starts Its Service

**Laptop 1 runs:**
```
docker run -e SERVICE_NAME=A -p 50051:50051 cst435docker-servicea
```
This starts a server on port 50051 listening for requests. When it receives a number, it multiplies by 2 and sends back.

**Laptop 2 runs:**
```
docker run -e SERVICE_NAME=B -p 50051:50051 cst435docker-serviceb
```
This waits for numbers from Service A, adds 10, and sends to Service C.

**Laptop 3 runs:**
```
docker run -e SERVICE_NAME=C -p 50051:50051 cst435docker-servicec
```
This waits for numbers from Service B, multiplies by 3, and sends back to client.

All three services run **simultaneously** and independently on their own machines.

---

### Step 2: Client Sends Requests

**Laptop 5 (Your Laptop) runs:**
```
python client/main.py \
  --targets "192.168.1.10:50051,192.168.1.11:50051,192.168.1.12:50051" \
  --requests 300 \
  --concurrency 10 \
  --work_ms 10 \
  --input 5
```

This tells the client:
- **targets**: IPs of the 3 services (Service A, B, C)
- **requests**: Send 300 total requests
- **concurrency**: Send 10 requests in parallel (10 at the same time)
- **work_ms**: Each service simulates 10ms of work
- **input**: Start each request with value 5

---

### Step 3: Request Flow (One Example Request)

```
Time 0ms:
  Client sends:  5
  ↓
  [Laptop 1] Service A receives 5
             → Multiplies by 2 → Result: 10
             → Sends 10 to Service B
             → Takes ~10ms (simulated work)

Time 10ms:
  [Laptop 2] Service B receives 10
             → Adds 10 → Result: 20
             → Sends 20 to Service C
             → Takes ~10ms (simulated work)

Time 20ms:
  [Laptop 3] Service C receives 20
             → Multiplies by 3 → Result: 60
             → Sends 60 back to client
             → Takes ~10ms (simulated work)

Time 30ms:
  Client receives:  60
  Total RTT (Round-Trip Time): 30ms
```

---

### Step 4: Parallel Requests

The client doesn't send requests one-at-a-time. It sends **10 in parallel**:

```
Request 1: [5 → 10 → 20 → 60]  (timeline 0-30ms)
Request 2: [5 → 10 → 20 → 60]  (timeline 0-30ms) - runs at same time!
Request 3: [5 → 10 → 20 → 60]  (timeline 0-30ms) - runs at same time!
... 10 total in parallel
```

This simulates **concurrent users** all using the system at once.

**Why?** Real systems have multiple users sending requests simultaneously. We want to see how the system handles this load.

---

## Data Collection: CSV Output

After all 300 requests complete, the client writes a **CSV file** with this data:

```
input, computed, transformed, final_result, service_a, service_b, service_c, send_ts, recv_ts, rtt_ms, error
```

| Column | Meaning |
|--------|---------|
| **input** | Input value (always 5 in our test) |
| **computed** | After Service A (5 × 2 = 10) |
| **transformed** | After Service B (10 + 10 = 20) |
| **final_result** | After Service C (20 × 3 = 60) |
| **service_a** | IP address of Service A |
| **service_b** | IP address of Service B |
| **service_c** | IP address of Service C |
| **send_ts** | Timestamp when client sent request (milliseconds) |
| **recv_ts** | Timestamp when client received response (milliseconds) |
| **rtt_ms** | Round-Trip Time = recv_ts - send_ts |
| **error** | If request failed, error message here |

**Example Row:**
```
5, 10, 20, 60, 192.168.1.10:50051, 192.168.1.11:50051, 192.168.1.12:50051, 1763126239680, 1763126239686, 6, 
```

This means:
- Request took **6 milliseconds** total
- All transformations worked correctly (5→10→20→60)
- No errors

---

## Key Concepts Explained

### Network Latency
When data travels between laptops over WiFi/Ethernet, it takes time. This is **network latency**.

- **Local system** (all on same machine): ~0-1ms latency
- **Distributed system** (across network): 5-50ms latency depending on network

**Why it matters**: Distributed systems are slower because of network travel time.

### Concurrency
Running multiple requests **at the same time** on the same system.

- **Sequential** (1 at a time): 300 requests × 30ms = 9000ms total
- **Concurrent** (10 at a time): 300 requests ÷ 10 = 30 batches × 30ms = 900ms total

Concurrency is **10x faster** in this case!

### Round-Trip Time (RTT)
The time from when the client **sends** a request until it **receives** the response.

RTT includes:
- Time traveling from Client → Service A
- Time Service A processes
- Time traveling A → B
- Time Service B processes
- Time traveling B → C
- Time Service C processes
- Time traveling C → Client

**Total = Network latency + Processing time**

### Throughput
How many requests complete per unit of time.

```
300 requests in 3000ms = 100 requests per second
```

---

## Experiment Timeline

### Before Running (Setup)

1. **Get IPs** from each laptop:
   ```powershell
   ipconfig
   ```

2. **Open firewall** on Laptops 1-3 (allow port 50051):
   ```powershell
   New-NetFirewallRule -DisplayName "Allow gRPC" -Direction Inbound -Protocol TCP -LocalPort 50051 -Action Allow
   ```

3. **Build images** on each laptop:
   ```powershell
   docker-compose build
   ```

### During Running (Execution)

4. **Start services** on Laptops 1-3 (keep terminals open):
   ```
   Laptop 1: docker run -e SERVICE_NAME=A -p 50051:50051 servicea
   Laptop 2: docker run -e SERVICE_NAME=B -p 50051:50051 serviceb
   Laptop 3: docker run -e SERVICE_NAME=C -p 50051:50051 servicec
   ```

5. **Run client** on Laptop 5 (your laptop):
   ```powershell
   python client/main.py --targets "192.168.1.10:50051,192.168.1.11:50051,192.168.1.12:50051" ...
   ```

### After Running (Analysis)

6. **Collect CSV** results on Laptop 5:
   ```
   results/results.csv → 300 rows of data
   ```

7. **Analyze**:
   - Average RTT across all requests
   - Min/Max RTT
   - Total time
   - Success rate (no errors)

---

## Real-World Applications

This experiment mimics many real systems:

### E-Commerce
```
Request → [Database Service] → [Payment Service] → [Shipping Service] → Response
```

### Video Streaming
```
Request → [Auth Service] → [Cache Service] → [Video Stream Service] → Response
```

### Weather App
```
Request → [Data Collection] → [Processing] → [Formatting] → Response
```

---

## Local vs Distributed Comparison

### Local Mode (All on One Machine)
```
docker-compose up --build
├─ Service A runs in container
├─ Service B runs in container  
├─ Service C runs in container
└─ All communicate via Docker network (fast, no real latency)
```

**Pros:** Fast to test, no setup needed
**Cons:** Doesn't test real network conditions

### Distributed Mode (5 Separate Laptops)
```
Laptop 1: Service A (192.168.1.10)
Laptop 2: Service B (192.168.1.11)
Laptop 3: Service C (192.168.1.12)
Laptop 5: Client (192.168.1.20)
```

**Pros:** Tests real network, realistic performance
**Cons:** More setup, slower, requires multiple machines

---

## Expected Results

For 300 requests with 10 concurrency and 10ms work per service:

```
=== Experiment Summary ===
Total requests: 300
Total time: 3245ms (3.25 seconds)
Average RTT per request: 10.82ms
Min RTT: 8ms
Max RTT: 25ms
```

**Analysis:**
- Each request should take ~30ms (3 services × 10ms each)
- Network adds ~0-5ms extra latency
- Some variation is normal (Min/Max difference)
- 300 requests in ~3 seconds = 100 requests/second throughput

---

## Teaching Tips

When explaining to others:

1. **Start with the assembly line analogy** — everyone understands factories
2. **Show the CSV data** — numbers are concrete
3. **Compare local vs distributed** — shows why we care
4. **Demo it live** — run one request and watch the CSV fill
5. **Ask questions** — "Why is RTT different for each request?"

### Good Questions to Ask

- "What happens if one service is slow?"
- "What if we increase concurrency to 50?"
- "How would RTT change if services were in different cities?"
- "Why can't we make requests faster than the network speed?"

---

## Summary

| Concept | Definition |
|---------|-----------|
| **Pipeline** | Sequence of services processing data one-by-one |
| **Distributed** | Services run on separate machines connected by network |
| **Concurrency** | Multiple requests processed at same time |
| **Latency** | Time for data to travel across network |
| **Throughput** | Requests completed per unit of time |
| **RTT** | Time from sending request to receiving response |
| **Scalability** | How well system handles more requests/machines |

---

## Next Steps for Students

1. Run the local version first (single machine) — easier to understand
2. Compare to distributed version — see the difference
3. Modify parameters (requests, concurrency, work_ms) — see effects
4. Add a 4th service — see how it scales
5. Run with 50 concurrent requests — watch throughput increase

This is how real engineers learn distributed systems!
