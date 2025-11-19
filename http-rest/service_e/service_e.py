#!/usr/bin/env python3
"""
HTTP/REST Service E - Currency Rounding
Part of the 5-stage distributed computing pipeline
"""

from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)
SERVICE_NAME = os.getenv('SERVICE_NAME', 'E')
WORK_MS = int(os.getenv('WORK_MS', '10'))
ROUND_BASE = int(os.getenv('ROUND_BASE', '5'))

def process_value(value):
    """Service E: Round down to nearest multiple of ROUND_BASE"""
    # Simulate work
    time.sleep(WORK_MS / 1000.0)
    return (value // ROUND_BASE) * ROUND_BASE

@app.route('/process', methods=['POST'])
def process():
    """Process a request: round value to nearest multiple of ROUND_BASE"""
    try:
        data = request.json or {}
        if 'value' not in data:
            return jsonify({
                "error": "Missing 'value' in request",
                "status": "error"
            }), 400
        
        input_value = int(data['value'])
        
        # Process the value
        result = process_value(input_value)
        
        return jsonify({
            "value": int(result),
            "service": SERVICE_NAME,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": f"service-{SERVICE_NAME}",
        "operation": f"currency rounding (nearest {ROUND_BASE})",
        "timestamp": time.time()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": f"Service {SERVICE_NAME}",
        "operation": f"Currency Rounding (nearest {ROUND_BASE})",
        "endpoints": {
            "POST /process": "Process a value (currency rounding)",
            "GET /health": "Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    print(f"Starting Service {SERVICE_NAME} (Currency Rounding) on port {port}...")
    print(f"Work simulation: {WORK_MS}ms per request")
    app.run(host='0.0.0.0', port=port, debug=False)

