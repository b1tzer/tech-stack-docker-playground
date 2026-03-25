import redis
import time
import random

# Connect to Redis Master
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def simulate_cache_avalanche():
    print("--- Simulating Cache Avalanche (Bad Practice) ---")
    # Set 100 keys to expire at the EXACT same time (10 seconds from now)
    for i in range(100):
        r.set(f"bad_key:{i}", "value", ex=10)
    print("Set 100 keys with exact 10s expiration.")
    
    print("\n--- Simulating Solution (Good Practice) ---")
    # Set 100 keys to expire with a random jitter (10 to 15 seconds)
    for i in range(100):
        jitter = random.randint(0, 5)
        r.set(f"good_key:{i}", "value", ex=10 + jitter)
    print("Set 100 keys with 10s + random(0-5)s expiration.")

if __name__ == "__main__":
    simulate_cache_avalanche()
    print("\nCheck Redis Commander or CLI to see the TTLs.")
