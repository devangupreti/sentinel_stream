import requests
import random
import time

URL = "http://127.0.0.1:8000/detect"

def run_test(n=50):
    print(f"🚀 Starting stress test with {n} requests...")
    for i in range(n):
        payload = {
            "transaction_id": f"tx_{i}",
            "user_id": f"user_{random.randint(1, 20)}", # Simulates 20 unique users
            "amount": random.uniform(10.0, 6000.0),
            "ip_address": f"192.168.1.{random.randint(1, 150)}"
        }
        resp = requests.post(URL, json=payload)
        data = resp.json()
        
        print(f"Req {i}: Status={data['status']} | Unique Users Estimated={data['user_stats']['unique_users_seen']}")
        time.sleep(0.1) # Small delay to see the logs

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Error: {e}. Is the server running?")