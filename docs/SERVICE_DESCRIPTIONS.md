# Service Descriptions - Distributed Pipeline

## Overview

This document describes the **5-stage distributed pipeline** that simulates a business order processing system. Each service performs a specific operation on the data and passes the result to the next service in the pipeline.

---

## Pipeline Architecture

```
Input Value
    ↓
[Service A: Inventory Check]
    ↓
[Service B: Sales Tax]
    ↓
[Service C: Shipping Calculation]
    ↓
[Service D: Processing Fee]
    ↓
[Service E: Currency Rounding]
    ↓
Final Result
```

---

## Service Details

### **Service A: Inventory Check**

**Purpose:** Add incoming stock to base inventory

**Operation:**
```
result = input_value + 100
```

**Business Logic:**
- Simulates adding new inventory items to existing base stock (100 units)
- Input represents incoming shipment quantity
- Output is total inventory after receiving shipment

**Example:**
```
Input:  5
Output: 105  (5 + 100)
```

**Port:** 50051 (gRPC) / 1099 (RMI)

---

### **Service B: Sales Tax Calculation**

**Purpose:** Apply 15% sales tax to the computed value

**Operation:**
```
result = int(computed_value × 1.15)
```

**Business Logic:**
- Calculates total price including 15% sales tax
- Represents tax applied to inventory value
- Integer conversion for currency rounding

**Example:**
```
Input:  105
Output: 120  (105 × 1.15 = 120.75 → 120)
```

**Port:** 50051 (gRPC) / 1099 (RMI)

---

### **Service C: Shipping Cost Calculation**

**Purpose:** Calculate shipping cost based on order size

**Operation:**
```
result = 50 + (transformed_value ÷ 10)
```

**Business Logic:**
- Base shipping cost: $50
- Additional cost: $1 per 10 units
- Models weight-based or volume-based shipping

**Example:**
```
Input:  120
Output: 62  (50 + 120÷10 = 50 + 12 = 62)
```

**Port:** 50051 (gRPC) / 1099 (RMI)

---

### **Service D: Processing Fee**

**Purpose:** Add 2.5% transaction processing fee

**Operation:**
```
result = int(aggregated_value × 1.025)
```

**Business Logic:**
- Applies payment processing fee (2.5%)
- Represents credit card or payment gateway charges
- Common in e-commerce systems

**Example:**
```
Input:  62
Output: 63  (62 × 1.025 = 63.55 → 63)
```

**Port:** 50051 (gRPC) / 1099 (RMI)

---

### **Service E: Currency Rounding**

**Purpose:** Round final amount to nearest $5 for invoicing

**Operation:**
```
result = (refined_value ÷ 5) × 5
```

**Business Logic:**
- Rounds down to nearest multiple of 5
- Simplifies invoicing and payment
- Common practice in wholesale or B2B transactions

**Example:**
```
Input:  63
Output: 60  ((63÷5) × 5 = 12 × 5 = 60)
```

**Port:** 50051 (gRPC) / 1099 (RMI)

---

## Complete Pipeline Example

**Input Value: 5**

| Stage | Service | Operation | Input | Output |
|-------|---------|-----------|-------|--------|
| 1 | Service A | Inventory Check | 5 | 105 |
| 2 | Service B | Sales Tax (15%) | 105 | 120 |
| 3 | Service C | Shipping Cost | 120 | 62 |
| 4 | Service D | Processing Fee (2.5%) | 62 | 63 |
| 5 | Service E | Currency Rounding | 63 | **60** |

**Final Result: 60**

---

## Service Communication

### **gRPC Implementation (Python)**

**Protocol:** Protocol Buffers over HTTP/2  
**Language:** Python 3.11  
**Port:** 50051 (internal), 50061-50065 (external)

**Communication Flow:**
```
Client → gRPC Stub → Service A (Compute)
       → gRPC Stub → Service B (Transform)
       → gRPC Stub → Service C (Aggregate)
       → gRPC Stub → Service D (Refine)
       → gRPC Stub → Service E (Finalize)
       → Result
```

### **RMI Implementation (Java)**

**Protocol:** Java Remote Method Invocation  
**Language:** Java 11  
**Port:** 1099 (internal), 1099-1103 (external)

**Communication Flow:**
```
Client → RMI Registry → Service A (compute)
       → RMI Registry → Service B (transform)
       → RMI Registry → Service C (aggregate)
       → RMI Registry → Service D (refine)
       → RMI Registry → Service E (finalize)
       → Result
```

---

## Service Configuration

Each service can be configured with:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `SERVICE_NAME` | Service identifier (A, B, C, D, or E) | Required |
| `PORT` | Service listening port | 50051 (gRPC), 1099 (RMI) |
| `work_ms` | Artificial delay to simulate processing time | 0 ms |

---

## Scalability & Distribution

### **Single Machine Deployment**
All 5 services run in Docker containers on one computer:
```bash
docker-compose up --build
```

### **Distributed Deployment**
Each service runs on a separate physical machine:
- **Laptop 1:** Service A
- **Laptop 2:** Service B
- **Laptop 3:** Service C
- **Laptop 4:** Service D
- **Laptop 5:** Service E
- **Client Machine:** Coordinates requests

---

## Performance Characteristics

### **Latency Factors**
1. **Network latency** between services
2. **Processing time** (configurable via `work_ms`)
3. **Serialization overhead** (Protocol Buffers vs Java serialization)
4. **Number of hops** (5 sequential service calls)

### **Parallelization**
- **Function Parallelization:** Multiple concurrent requests processed by worker threads
- **Concurrency Level:** 10 workers (default)
- **Throughput:** ~300 requests in ~1.8 seconds (local mode)

### **Typical Performance (Local)**
- **Average RTT:** 55-60ms per request
- **Min RTT:** 50ms
- **Max RTT:** 70ms
- **Total Time (300 req):** 1.8-2.0 seconds

---

## Use Cases

This pipeline architecture is representative of:

1. **E-commerce Order Processing**
   - Inventory validation → Tax calculation → Shipping → Payment processing → Invoicing

2. **Supply Chain Management**
   - Stock updates → Cost calculation → Logistics → Fees → Final pricing

3. **Financial Transactions**
   - Account balance → Interest calculation → Fees → Processing → Rounding

4. **Data Processing Pipelines**
   - Validation → Transformation → Aggregation → Refinement → Formatting

---

## Error Handling

Each service includes error handling for:
- **Network failures:** Connection timeouts, unavailable services
- **Invalid inputs:** Type mismatches, null values
- **Service unavailability:** Service not bound in registry

Errors are captured in the `error` column of the CSV output file.

---

## Monitoring & Results

### **CSV Output Format**
```csv
input,computed,transformed,aggregated,refined,final_result,service_a,service_b,service_c,service_d,service_e,send_ts,recv_ts,rtt_ms,error
5,105,120,62,63,60,servicea:50051,serviceb:50051,servicec:50051,serviced:50051,servicee:50051,1763483586861,1763483586925,64,
```

### **Metrics Tracked**
- Input and output values for each stage
- Service endpoints used
- Send and receive timestamps
- Round-trip time (RTT) in milliseconds
- Error messages (if any)

---

## Extending the Pipeline

To add a new service (Service F):

1. **Define new RPC method** in proto file (gRPC) or interface (RMI)
2. **Implement service logic** in server code
3. **Update docker-compose.yml** with new service container
4. **Modify client** to include Service F in pipeline
5. **Update port mappings** (e.g., 50066 for gRPC)

---

## References

- **gRPC Documentation:** https://grpc.io/docs/languages/python/
- **RMI Tutorial:** https://docs.oracle.com/javase/tutorial/rmi/
- **Protocol Buffers:** https://protobuf.dev/
- **Docker Compose:** https://docs.docker.com/compose/

---

**Last Updated:** November 19, 2025  
**Project:** CST 435 Distributed Systems Experiment
