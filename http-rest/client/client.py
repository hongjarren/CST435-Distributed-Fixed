#!/usr/bin/env python3
"""
HTTP/REST Client - Sends requests through the 5-stage business pipeline
Follows the service flow defined in SERVICE_DESCRIPTIONS.md
"""

import requests
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import csv
import argparse
import concurrent.futures
import random
import sys
from typing import List, Dict
import os

STAGE_KEYS = [
    ("computed", "service_a"),
    ("transformed", "service_b"),
    ("aggregated", "service_c"),
    ("refined", "service_d"),
    ("final_result", "service_e"),
]

# Try to force line-buffering of stdout so prints appear promptly in terminals
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(line_buffering=True)
except Exception:
    # best-effort only; continue if not supported
    pass

# Thread-local session to enable connection pooling per worker thread
thread_local = threading.local()

# Shared session used when created by run_experiment. Kept global so all threads reuse same pool.
_shared_session = None

def create_shared_session(pool_maxsize: int = 10, pool_connections: int = 10, retries: int = 3) -> requests.Session:
    """Create a shared requests.Session with a pooled HTTPAdapter and retries/backoff.

    Args:
        pool_maxsize: maximum connections per host pool (important for concurrency)
        pool_connections: number of host pools to keep
        retries: total retry attempts for idempotent/transient errors
    """
    global _shared_session
    if _shared_session is None:
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        )
        adapter = HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'Connection': 'keep-alive'})
        _shared_session = session
    return _shared_session


def get_session() -> requests.Session:
    """Return the shared session if created, otherwise a thread-local session.

    The shared session should be created at the start of the experiment by
    calling `create_shared_session(concurrency)` from `run_experiment`.
    """
    global _shared_session
    if _shared_session is not None:
        return _shared_session
    # Fallback: thread-local session (keeps previous behavior if shared not created)
    if not hasattr(thread_local, 'session'):
        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'Connection': 'keep-alive'})
        thread_local.session = session
    return thread_local.session

# Per-call retry/backoff settings
DEFAULT_CALL_RETRIES = 5
CALL_BACKOFF_FACTOR = 0.5
CALL_JITTER = 0.1

def call_service(url: str, value: int) -> int:
    """Invoke a service endpoint and return the computed value."""
    session = get_session()

    last_exc = None
    for attempt in range(1, DEFAULT_CALL_RETRIES + 1):
        try:
            response = session.post(
                f"{url}/process",
                json={"value": value},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.RequestException as e:
            last_exc = e
            # If this was the last attempt, re-raise and let the caller handle it
            if attempt == DEFAULT_CALL_RETRIES:
                raise
            # Backoff with jitter
            backoff = CALL_BACKOFF_FACTOR * (2 ** (attempt - 1))
            time.sleep(backoff + random.uniform(0, CALL_JITTER))

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
                  work_ms: int, input_value: int, output_file: str = "results.csv", max_outstanding: int = None):
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
    
    print("=== HTTP/REST Distributed Computing Experiment ===", flush=True)
    for label, url in zip(["Service A", "Service B", "Service C", "Service D", "Service E"], target_list):
        print(f"{label} URL: {url}", flush=True)
    print(f"Total requests: {requests_count}", flush=True)
    print(f"Concurrency: {concurrency}", flush=True)
    print(f"Work simulation: {work_ms}ms per service", flush=True)
    print(f"Input value: {input_value}", flush=True)
    print(flush=True)
    
    # Create shared session with pool sized to concurrency, then check service health
    create_shared_session(pool_maxsize=concurrency, pool_connections=10, retries=3)
    print("Checking service health...", flush=True)
    health_session = get_session()
    for name, url in zip(
        ["Service A", "Service B", "Service C", "Service D", "Service E"],
        target_list
    ):
        try:
            response = health_session.get(f"{url}/health", timeout=5)
            response.raise_for_status()
            print(f"  ✓ {name} is healthy", flush=True)
        except Exception as e:
            print(f"  ✗ {name} health check failed: {e}", flush=True)
            print(f"    Warning: Continuing anyway...", flush=True)
    print()
    
    # Create results directory if it doesn't exist (in parent directory)
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, output_file)
    
    # Prepare submission bounding (limit how many requests are submitted but not yet completed)
    if max_outstanding is None:
        max_outstanding = concurrency * 20
    semaphore = threading.Semaphore(max_outstanding)

    # Run experiment
    print("Starting experiment...", flush=True)
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all requests
        futures = []
        for i in range(requests_count):
            semaphore.acquire()
            future = executor.submit(
                process_request,
                target_list,
                input_value
            )
            # release the semaphore when the future finishes
            future.add_done_callback(lambda f, sem=semaphore: sem.release())
            futures.append(future)
        
        # Collect results as they complete
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            if completed % 50 == 0:
                print(f"  Completed {completed}/{requests_count} requests...", flush=True)
    
    total_time = time.time() - start_time
    
    # Write results to CSV
    print(f"\nWriting results to {output_path}...", flush=True)
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
    
    print("\n=== Experiment Summary ===", flush=True)
    print(f"Total requests: {requests_count}", flush=True)
    print(f"Successful requests: {len(successful)}", flush=True)
    print(f"Failed requests: {len(results) - len(successful)}", flush=True)
    print(f"Total time: {total_time:.2f} seconds ({total_time*1000:.2f}ms)", flush=True)
    
    if rtts:
        print(f"Average RTT per request: {sum(rtts)/len(rtts):.2f}ms", flush=True)
        print(f"Min RTT: {min(rtts)}ms", flush=True)
        print(f"Max RTT: {max(rtts)}ms", flush=True)
        print(f"Throughput: {len(successful)/total_time:.2f} requests/second", flush=True)
    
    print(f"\nResults saved to: {output_path}", flush=True)
    
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
    parser.add_argument('--max-outstanding', type=int, default=None,
                       help='Maximum submitted-but-not-completed requests (defaults to concurrency*20)')
    
    args = parser.parse_args()
    
    run_experiment(
        targets=args.targets,
        requests_count=args.requests,
        concurrency=args.concurrency,
        work_ms=args.work_ms,
        input_value=args.input,
        output_file=args.output,
        max_outstanding=args.max_outstanding
    )

