import requests
import time

def test_passenger_cache_performance():
    url = "http://127.0.0.1:8000/api/users/passengers/"
    
    # First call (cache miss)
    start = time.time()
    response1 = requests.get(url)
    time1 = time.time() - start
    
    # Second call (cache hit)
    start = time.time()
    response2 = requests.get(url)
    time2 = time.time() - start
    
    print(f"First call: {time1:.4f}s")
    print(f"Second call: {time2:.4f}s")
    print(f"Speedup: {time1/time2:.2f}x")

if __name__ == "__main__":
    test_passenger_cache_performance()
