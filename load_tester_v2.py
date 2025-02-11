import requests
import time
import threading
from flask import Flask, request, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

tester = Flask("tester_service")

# Create histograms to measure request latency for each endpoint.
deposit_latency_histogram = Histogram(
    'loadtester_deposit_latency_seconds',
    'Latency for deposit requests'
)
withdraw_latency_histogram = Histogram(
    'loadtester_withdraw_latency_seconds',
    'Latency for withdraw requests'
)


class LoadTester:
    def __init__(self, front_url, interval=60):
        self.front_url = front_url
        self.interval = interval  # Time between request cycles (in seconds)

    def send_requests(self):
        while True:
            # Time the deposit request.
            with deposit_latency_histogram.time():
                requests.post(f"{self.front_url}/deposit", json={"amount": 100})

            # Time the withdraw request.
            with withdraw_latency_histogram.time():
                requests.post(f"{self.front_url}/withdraw", json={"amount": 50})

            # Wait for the defined interval before sending the next requests.
            time.sleep(self.interval)

    def start(self):
        threads = []
        for _ in range(10):  # Simulating 10 concurrent users
            t = threading.Thread(target=self.send_requests)
            t.daemon = True  # Optional: mark threads as daemon so they exit when the main thread exits
            t.start()
            threads.append(t)
        # Since the threads run an infinite loop, we can join them to keep the main thread alive.
        for t in threads:
            t.join()


@tester.route("/metrics", methods=["GET"])
def metrics():
    """
    Expose Prometheus metrics.
    The Prometheus server will scrape this endpoint at configured intervals.
    """
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    # Initialize the load tester with the front service URL and a 60-second interval.
    load_tester = LoadTester("http://front:5002", interval=60)

    # Start the load tester in a separate background thread so that it runs concurrently with the Flask app.
    load_tester_thread = threading.Thread(target=load_tester.start)
    load_tester_thread.daemon = True  # Optional: ensures that the thread will exit when the main process does
    load_tester_thread.start()

    # Start the Flask service to expose metrics on port 5003.
    print("[INFO] Starting the tester service on port 5003...")
    tester.run(host="0.0.0.0", port=5003)
