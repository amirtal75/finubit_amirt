import requests
import time
import threading


class LoadTester:
    def __init__(self, front_url, duration=100):
        self.front_url = front_url
        self.duration = duration
        self.start_time = time.time()

    def send_requests(self):
        while time.time() - self.start_time < self.duration:
            requests.post(f"{self.front_url}/deposit", json={"amount": 100})
            requests.post(f"{self.front_url}/withdraw", json={"amount": 50})
            time.sleep(5)

    def start(self):
        threads = []
        for _ in range(10):  # Simulating multiple users
            t = threading.Thread(target=self.send_requests)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()


if __name__ == "__main__":
    tester = LoadTester("http://front:5002")
    tester.start()
