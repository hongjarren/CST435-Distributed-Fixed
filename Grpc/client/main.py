import grpc
import compute_pb2
import compute_pb2_grpc
import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


PORT_DEFAULT = 50051


def pipeline_call(service_a, service_b, service_c, input_value, work_ms, timeout=10):
    """
    Execute the pipeline: 
    1. Call service_a.Compute(value) -> computed_result
    2. Call service_b.Transform(computed_result) -> transformed_result
    3. Call service_c.Aggregate(transformed_result) -> final_result
    """
    try:
        send_ts = int(time.time() * 1000)
        
        # Step 1: Service A - Compute
        chan_a = grpc.insecure_channel(service_a)
        stub_a = compute_pb2_grpc.ComputeStub(chan_a)
        req_a = compute_pb2.ComputeRequest(value=input_value, work_ms=work_ms)
        resp_a = stub_a.Compute(req_a, timeout=timeout)
        computed_value = resp_a.result
        
        # Step 2: Service B - Transform
        chan_b = grpc.insecure_channel(service_b)
        stub_b = compute_pb2_grpc.ComputeStub(chan_b)
        req_b = compute_pb2.TransformRequest(computed_value=computed_value, work_ms=work_ms)
        resp_b = stub_b.Transform(req_b, timeout=timeout)
        transformed_value = resp_b.result
        
        # Step 3: Service C - Aggregate
        chan_c = grpc.insecure_channel(service_c)
        stub_c = compute_pb2_grpc.ComputeStub(chan_c)
        req_c = compute_pb2.AggregateRequest(transformed_value=transformed_value, work_ms=work_ms)
        resp_c = stub_c.Aggregate(req_c, timeout=timeout)
        final_result = resp_c.final_result
        
        recv_ts = int(time.time() * 1000)
        rtt = recv_ts - send_ts
        
        return {
            'input': input_value,
            'computed': computed_value,
            'transformed': transformed_value,
            'final_result': final_result,
            'service_a': service_a,
            'service_b': service_b,
            'service_c': service_c,
            'send_ts': send_ts,
            'recv_ts': recv_ts,
            'rtt_ms': rtt,
            'error': ''
        }
    except Exception as e:
        recv_ts = int(time.time() * 1000)
        return {
            'input': input_value,
            'computed': None,
            'transformed': None,
            'final_result': None,
            'service_a': service_a,
            'service_b': service_b,
            'service_c': service_c,
            'send_ts': send_ts if 'send_ts' in locals() else None,
            'recv_ts': recv_ts,
            'rtt_ms': None,
            'error': str(e)
        }


def worker(service_a, service_b, service_c, n, input_value, work_ms):
    rows = []
    for i in range(n):
        row = pipeline_call(service_a, service_b, service_c, input_value, work_ms)
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', required=True, help='comma-separated list of service_a:port,service_b:port,service_c:port')
    parser.add_argument('--requests', type=int, default=100, help='total requests per pipeline')
    parser.add_argument('--concurrency', type=int, default=10)
    parser.add_argument('--work_ms', type=int, default=0)
    parser.add_argument('--input', type=int, default=5, help='input value for computation')
    parser.add_argument('--out', type=str, default='/tmp/results.csv')
    args = parser.parse_args()

    # Parse targets: "servicea:50051,serviceb:50051,servicec:50051"
    targets = [t.strip() for t in args.targets.split(',') if t.strip()]
    if len(targets) != 3:
        print("ERROR: Expected 3 targets (service_a, service_b, service_c)")
        return
    
    service_a, service_b, service_c = targets

    # Split requests across concurrency
    per_thread = max(1, args.requests // args.concurrency)

    all_rows = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = []
        for i in range(args.concurrency):
            futures.append(ex.submit(worker, service_a, service_b, service_c, per_thread, args.input, args.work_ms))

        for fut in as_completed(futures):
            try:
                rows = fut.result()
                all_rows.extend(rows)
            except Exception as e:
                print("worker failed:", e)

    # Write CSV
    fieldnames = ['input', 'computed', 'transformed', 'final_result', 'service_a', 'service_b', 'service_c', 'send_ts', 'recv_ts', 'rtt_ms', 'error']
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)

    # Calculate total experiment time
    all_rows_with_ts = [r for r in all_rows if r['send_ts'] and r['recv_ts']]
    if all_rows_with_ts:
        first_send = min(r['send_ts'] for r in all_rows_with_ts)
        last_recv = max(r['recv_ts'] for r in all_rows_with_ts)
        total_time_ms = last_recv - first_send
        total_time_sec = total_time_ms / 1000
        
        avg_rtt = sum(r['rtt_ms'] for r in all_rows_with_ts if r['rtt_ms']) / len([r for r in all_rows_with_ts if r['rtt_ms']])
        
        print(f"\n=== Experiment Summary ===")
        print(f"Total requests: {len(all_rows)}")
        print(f"Total time: {total_time_ms}ms ({total_time_sec:.2f}s)")
        print(f"Average RTT per request: {avg_rtt:.2f}ms")
        print(f"Min RTT: {min(r['rtt_ms'] for r in all_rows_with_ts if r['rtt_ms']):.2f}ms")
        print(f"Max RTT: {max(r['rtt_ms'] for r in all_rows_with_ts if r['rtt_ms']):.2f}ms")

    print(f"Wrote {len(all_rows)} rows to {args.out}")


if __name__ == '__main__':
    main()
