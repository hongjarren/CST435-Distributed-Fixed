#!/usr/bin/env python3
"""
HTTP/REST Client - Sends requests through the 5-stage business pipeline
Follows the service flow defined in SERVICE_DESCRIPTIONS.md
"""

import requests
import time
import csv
import argparse
import concurrent.futures
from typing import List, Dict
import os

STAGE_KEYS = [
    ("computed", "service_a"),
    ("transformed", "service_b"),
    ("aggregated", "service_c"),
    ("refined", "service_d"),
    ("final_result", "service_e"),
]

def call_service(url: str, value: int) -> int:
    """Invoke a service endpoint and return the computed value."""
    response = requests.post(
        f"{url}/process",
        json={"value": value},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    if "value" not in data:
        raise ValueError(f"Service at {url} returned no 'value'")
    return int(data["value"])

def process_request(service_urls: List[str], input_value: int) -> Dict:
    """
    Process a single request through the 5-stage pipeline:
    Service A (Inventory) -> B (Sales Tax) -> C (Shipping) -> D (Processing Fee) -> E (Currency Rounding)
    """
    send_ts = int(time.time() * 1000)  # milliseconds
    stage_values = {key: None for key, _ in STAGE_KEYS}
    service_mapping = {
        "service_a": service_urls[0],
        "service_b": service_urls[1],
        "service_c": service_urls[2],
        "service_d": service_urls[3],
        "service_e": service_urls[4],
    }
    
    try:
        current_value = input_value
        for index, (value_key, service_key) in enumerate(STAGE_KEYS):
            service_url = service_urls[index]
            current_value = call_service(service_url, current_value)
            stage_values[value_key] = current_value
        
        recv_ts = int(time.time() * 1000)  # milliseconds
        rtt_ms = recv_ts - send_ts
        
        return {
            "input": input_value,
            **stage_values,
            **service_mapping,
            "send_ts": send_ts,
            "recv_ts": recv_ts,
            "rtt_ms": rtt_ms,
            "error": ""
        }
        
    except Exception as e:
        recv_ts = int(time.time() * 1000)
        return {
            "input": input_value,
            **stage_values,
            **service_mapping,
            "send_ts": send_ts,
            "recv_ts": recv_ts,
            "rtt_ms": recv_ts - send_ts,
            "error": str(e)
        }

def run_experiment(targets: str, requests_count: int, concurrency: int, 
                  work_ms: int, input_value: int, output_file: str = "results.csv"):
    """
    Run the distributed computing experiment
    
    Args:
        targets: Comma-separated URLs for Service A-E (e.g., "http://192.168.1.10:5000,...,http://192.168.1.14:5000")
        requests_count: Total number of requests to send
        concurrency: Number of parallel requests
        work_ms: Work simulation time per service (ms)
        input_value: Input value for each request
        output_file: CSV file to write results
    """
    # Parse targets
    target_list = [url.strip() for url in targets.split(",")]
    if len(target_list) != 5:
        raise ValueError("Must provide exactly 5 targets (Services A-E)")
    
    print("=== HTTP/REST Distributed Computing Experiment ===")
    for label, url in zip(["Service A", "Service B", "Service C", "Service D", "Service E"], target_list):
        print(f"{label} URL: {url}")
    print(f"Total requests: {requests_count}")
    print(f"Concurrency: {concurrency}")
    print(f"Work simulation: {work_ms}ms per service")
    print(f"Input value: {input_value}")
    print()
    
    # Check service health
    print("Checking service health...")
    for name, url in zip(
        ["Service A", "Service B", "Service C", "Service D", "Service E"],
        target_list
    ):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            response.raise_for_status()
            print(f"  ✓ {name} is healthy")
        except Exception as e:
            print(f"  ✗ {name} health check failed: {e}")
            print(f"    Warning: Continuing anyway...")
    print()
    
    # Create results directory if it doesn't exist (in parent directory)
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, output_file)
    
    # Run experiment
    print("Starting experiment...")
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all requests
        futures = []
        for i in range(requests_count):
            future = executor.submit(
                process_request,
                target_list,
                input_value
            )
            futures.append(future)
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            if completed % 50 == 0:
                print(f"  Completed {completed}/{requests_count} requests...")
    
    total_time = time.time() - start_time
    
    # Write results to CSV
    print(f"\nWriting results to {output_path}...")
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'input', 'computed', 'transformed', 'aggregated', 'refined', 'final_result',
            'service_a', 'service_b', 'service_c', 'service_d', 'service_e',
            'send_ts', 'recv_ts', 'rtt_ms', 'error'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Calculate statistics
    successful = [r for r in results if not r['error']]
    rtts = [r['rtt_ms'] for r in successful]
    
    print("\n=== Experiment Summary ===")
    print(f"Total requests: {requests_count}")
    print(f"Successful requests: {len(successful)}")
    print(f"Failed requests: {len(results) - len(successful)}")
    print(f"Total time: {total_time:.2f} seconds ({total_time*1000:.2f}ms)")
    
    if rtts:
        print(f"Average RTT per request: {sum(rtts)/len(rtts):.2f}ms")
        print(f"Min RTT: {min(rtts)}ms")
        print(f"Max RTT: {max(rtts)}ms")
        print(f"Throughput: {len(successful)/total_time:.2f} requests/second")
    
    print(f"\nResults saved to: {output_path}")
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP/REST Distributed Computing Client')
    parser.add_argument('--targets', type=str, required=True,
                       help='Comma-separated URLs for Service A-E (e.g., "http://192.168.1.10:5000,...,http://192.168.1.14:5000")')
    parser.add_argument('--requests', type=int, default=300,
                       help='Total number of requests (default: 300)')
    parser.add_argument('--concurrency', type=int, default=10,
                       help='Number of parallel requests (default: 10)')
    parser.add_argument('--work_ms', type=int, default=10,
                       help='Work simulation time per service in ms (default: 10)')
    parser.add_argument('--input', type=int, default=5,
                       help='Input value for each request (default: 5)')
    parser.add_argument('--output', type=str, default='results.csv',
                       help='Output CSV filename (default: results.csv)')
    
    args = parser.parse_args()
    
    run_experiment(
        targets=args.targets,
        requests_count=args.requests,
        concurrency=args.concurrency,
        work_ms=args.work_ms,
        input_value=args.input,
        output_file=args.output
    )

