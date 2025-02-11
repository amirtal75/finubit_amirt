"""
core_service.py

This is the core bank service, which maintains an account balance and
processes deposit/withdraw requests. It also exposes Prometheus metrics
to allow monitoring of request counts, error rates, and request latency.

Key metrics:
  1) Number of deposit requests
  2) Number of withdraw requests
  3) Number of 4xx errors
  4) Number of 5xx errors
  5) Processing latency (Histogram) per action
  6) /metrics endpoint for Prometheus

Usage:
  1) Run this script: python core_service.py
  2) Access deposit/withdraw by POSTing JSON to http://localhost:5001/coreAPI
     Example JSON: {"action": "deposit", "amount": 100}
  3) View metrics at http://localhost:5001/metrics
"""

from flask import Flask, request, jsonify
import time
from prometheus_client import CONTENT_TYPE_LATEST

# Prometheus imports
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest
)

core = Flask("core_service")
account_balance = 0

# -----------------------------
# Prometheus Metrics
# -----------------------------

CORE_DEPOSIT_COUNTER = Counter(
    'core_deposit_requests_total',
    'Total number of deposit requests handled by the core service'
)
CORE_WITHDRAW_COUNTER = Counter(
    'core_withdraw_requests_total',
    'Total number of withdraw requests handled by the core service'
)

ERROR_4XX_COUNTER = Counter(
    'core_4xx_errors_total',
    'Total number of 4xx errors returned by the core service'
)
ERROR_5XX_COUNTER = Counter(
    'core_5xx_errors_total',
    'Total number of 5xx errors returned by the core service'
)

WITHDRAW_PROCESSING_TIME = Histogram(
    'core_withdraw_latency_seconds',
    'Withdraw latency for the core service',
    ['action']
)

DEPOSIT_PROCESSING_TIME = Histogram(
    'core_deposit_latency_seconds',
    'Deposit latency for the core service',
    ['action']
)

# -----------------------------
# Routes
# -----------------------------

@core.route("/coreAPI", methods=["POST"])
def core_api():
    """
    Handle deposit or withdraw requests:
      - deposit: increments the account balance
      - withdraw: (intentionally slow) decrements the account balance if sufficient funds

    JSON body format:
      {
        "action": "deposit" or "withdraw",
        "amount": <numeric>
      }

    Returns:
      200 with current/new balance or success message
      400 with error message if invalid action or insufficient funds
    """
    global account_balance
    start_time = time.time()

    # Parse request
    data = request.json or {}
    action = data.get("action")
    amount = data.get("amount", 0)

    # Debug print
    print(f"[DEBUG] Action: {action}, Amount: {amount}, Current Balance: {account_balance}")

    # Action logic
    if action == "deposit":
        CORE_DEPOSIT_COUNTER.inc()
        account_balance += amount
        status_code = 200
        response_body = {"new_balance": account_balance}
        duration = time.time() - start_time
        DEPOSIT_PROCESSING_TIME.labels(action=action).observe(duration)

    elif action == "withdraw":
        # Simulate slow request
        CORE_WITHDRAW_COUNTER.inc()
        time.sleep(5)

        if amount <= account_balance:
            account_balance -= amount
            status_code = 200
            response_body = {"message": "OK", "new_balance": account_balance}
            duration = time.time() - start_time
            WITHDRAW_PROCESSING_TIME.labels(action=action).observe(duration)
        else:
            # 4xx error due to insufficient funds
            status_code = 400
            response_body = {"error": "Insufficient funds"}


    else:
        # Invalid action (4xx error)
        status_code = 400
        response_body = {"error": "Invalid action"}

    # Measure the duration

    # Record to Prometheus histogram, label by action


    # Check and increment error counters if needed
    if 400 <= status_code < 500:
        ERROR_4XX_COUNTER.inc()
    elif 500 <= status_code < 600:
        ERROR_5XX_COUNTER.inc()

    print(f"[DEBUG] Action: {action}, Response: {response_body}, Status: {status_code}, Time: {duration:.4f}s")

    return jsonify(response_body), status_code


@core.route("/metrics", methods=["GET"])
def metrics():
    """
    Expose Prometheus metrics.
    The Prometheus server will scrape this endpoint at configured intervals.
    """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print("[INFO] Starting the core service on port 5001...")
    core.run(host="0.0.0.0", port=5001)
