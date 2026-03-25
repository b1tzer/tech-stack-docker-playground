import redis
import time
import threading
import uuid

# Connect to Redis Master
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def acquire_lock(lock_name, acquire_timeout=10, lock_timeout=10):
    """Attempt to acquire a distributed lock."""
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_timeout
    while time.time() < end:
        # NX: Set only if not exists. EX: Expire in seconds.
        if r.set(lock_name, identifier, nx=True, ex=lock_timeout):
            return identifier
        time.sleep(0.1) # Wait before retrying
    return False

def release_lock(lock_name, identifier):
    """Release the lock only if the identifier matches (to avoid releasing someone else's lock)."""
    # Use a Lua script to ensure atomicity (check and delete)
    lua_script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    result = r.eval(lua_script, 1, lock_name, identifier)
    return result == 1

def worker(worker_id):
    lock_name = "my_resource_lock"
    print(f"Worker {worker_id} trying to acquire lock...")
    
    identifier = acquire_lock(lock_name, acquire_timeout=5, lock_timeout=5)
    
    if identifier:
        print(f"Worker {worker_id} ACQUIRED lock! Doing work...")
        time.sleep(2) # Simulate doing some critical work
        print(f"Worker {worker_id} finished work. Releasing lock...")
        release_lock(lock_name, identifier)
    else:
        print(f"Worker {worker_id} FAILED to acquire lock (timeout).")

if __name__ == "__main__":
    print("--- Simulating Distributed Lock ---")
    # Start 3 threads trying to grab the same lock
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
