#!/usr/bin/env python3
"""
HTTP/REST Service B - Sales Tax Calculation (15%)
Part of the 5-stage distributed computing pipeline
"""

from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)
SERVICE_NAME = os.getenv('SERVICE_NAME', 'B')
WORK_MS = int(os.getenv('WORK_MS', '10'))
TAX_RATE = float(os.getenv('TAX_RATE', '0.15'))

def process_value(value):
    """Service B: Apply sales tax"""
    # Simulate work
    time.sleep(WORK_MS / 1000.0)
    return int(value * (1 + TAX_RATE))

@app.route('/process', methods=['POST'])
def process():
    """Process a request: apply 15% sales tax"""
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
        "operation": "sales tax (15%)",
        "timestamp": time.time()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": f"Service {SERVICE_NAME}",
        "operation": "Sales Tax (15%)",
        "endpoints": {
            "POST /process": "Process a value (add 15% tax)",
            "GET /health": "Health check"
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    print(f"Starting Service {SERVICE_NAME} (Add 10) on port {port}...")
    print(f"Work simulation: {WORK_MS}ms per request")
    app.run(host='0.0.0.0', port=port, debug=False)

