"""
front_service.py

This front service acts as an interface for a bank, forwarding deposit/withdraw
requests to the core microservice while also exposing Prometheus metrics for
monitoring purposes.

Metrics collected:
  1) Number of deposit requests
  2) Number of withdraw requests
  3) Number of 4xx errors
  4) Number of 5xx errors
  5) Processing latency (Histogram) per endpoint
  6) A /metrics endpoint for Prometheus scraping

Usage:
  1) Run this script: python front_service.py
  2) Access deposit or withdraw endpoints (POST) at http://localhost:5002/deposit or /withdraw
  3) View metrics at http://localhost:5002/metrics
"""

from flask import Flask, request, jsonify
import requests
import time
from prometheus_client import CONTENT_TYPE_LATEST


# Prometheus imports
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest
)

front = Flask("front_service")

# URL to your core microservice
CORE_URL = "http://core:5001/coreAPI"

# -----------------------------
# Prometheus Metrics
# -----------------------------

# Counters to track how many times each endpoint was called
DEPOSIT_COUNTER = Counter(
    'front_deposit_requests_total',
    'Total number of deposit requests handled by the front service'
)
WITHDRAW_COUNTER = Counter(
    'front_withdraw_requests_total',
    'Total number of withdraw requests handled by the front service'
)

# Counters to track 4xx and 5xx errors
ERROR_4XX_COUNTER = Counter(
    'front_4xx_errors_total',
    'Total number of 4xx errors returned by the front service'
)
ERROR_5XX_COUNTER = Counter(
    'front_5xx_errors_total',
    'Total number of 5xx errors returned by the front service'
)

# Histogram to measure the duration of requests for each endpoint
WITHDRAW_LATENCY = Histogram(
    'front_withdraw_latency_seconds',
    'Withdraw latency for the front service',
    ['endpoint']
)

DEPOSIT_LATENCY = Histogram(
    'front_deposit_latency_seconds',
    'Deposit latency for the front service',
    ['endpoint']
)


# -----------------------------
# Routes
# -----------------------------

@front.route("/deposit", methods=["POST"])
def deposit():
    """
    Handle a deposit request by forwarding it to the core service.

    Returns:
        JSON response from the core service, and the corresponding HTTP status code.
    """
    start_time = time.time()
    DEPOSIT_COUNTER.inc()  # Increment the deposit counter

    # Extract deposit amount from JSON body
    amount = request.json.get("amount", 0)
    print(f"[DEBUG] Deposit request received. Amount: {amount}")

    # Forward request to the core microservice
    response = requests.post(CORE_URL, json={"action": "deposit", "amount": amount})

    # Measure the duration
    duration = time.time() - start_time
    DEPOSIT_LATENCY.labels(endpoint='deposit').observe(duration)
    print(f"[DEBUG] Deposit processing finished in {duration:.4f} seconds. Status: {response.status_code}")

    # Check if the response is an error (4xx or 5xx), increment counters accordingly
    if 400 <= response.status_code < 500:
        ERROR_4XX_COUNTER.inc()
    elif 500 <= response.status_code < 600:
        ERROR_5XX_COUNTER.inc()

    return jsonify(response.json()), response.status_code


@front.route("/withdraw", methods=["POST"])
def withdraw():
    """
    Handle a withdraw request by forwarding it to the core service.

    Returns:
        JSON response from the core service, and the corresponding HTTP status code.
    """
    start_time = time.time()
    WITHDRAW_COUNTER.inc()  # Increment the withdraw counter

    # Extract withdraw amount from JSON body
    amount = request.json.get("amount", 0)
    print(f"[DEBUG] Withdraw request received. Amount: {amount}")

    # Forward request to the core microservice
    response = requests.post(CORE_URL, json={"action": "withdraw", "amount": amount})

    # Measure the duration
    duration = time.time() - start_time
    WITHDRAW_LATENCY.labels(endpoint='withdraw').observe(duration)
    print(f"[DEBUG] Withdraw processing finished in {duration:.4f} seconds. Status: {response.status_code}")

    # Check if the response is an error (4xx or 5xx), increment counters accordingly
    if 400 <= response.status_code < 500:
        ERROR_4XX_COUNTER.inc()
    elif 500 <= response.status_code < 600:
        ERROR_5XX_COUNTER.inc()

    return jsonify(response.json()), response.status_code


@front.route("/metrics", methods=["GET"])
def metrics():
    """
    Expose Prometheus metrics.
    The Prometheus server will scrape this endpoint at configured intervals.

    Returns:
        A plaintext response containing current metrics in Prometheus format.
    """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}



# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # Run the Flask app on port 5002, accessible from any host.
    print("[INFO] Starting the front service on port 5002...")
    front.run(host="0.0.0.0", port=5002)
