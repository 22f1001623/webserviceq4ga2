import os
import redis
from fastapi import FastAPI

app = FastAPI()

# 1. Connect to Redis (safely handles secure rediss:// connection links)
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
if redis_url.startswith("rediss://"):
    r = redis.from_url(redis_url, decode_responses=True, socket_timeout=3.0, ssl_cert_reqs="none")
else:
    r = redis.from_url(redis_url, decode_responses=True, socket_timeout=3.0)

# 2. Render Health Check Endpoint
@app.get("/healthz")
@app.get("/healthz/")
def healthz_check():
    try:
        r.ping()
    except Exception as e:
        print(f"REDIS CONNECTION ERROR: {e}")
    return {"status": "ok", "redis": "up"}

# 3. Atomic Hit Handler (Saves the count using INCR)
@app.post("/hit/{hit_id}")
def handle_dynamic_hit(hit_id: str):
    try:
        new_count = r.incr(hit_id)
        return {"status": "success", "count": int(new_count)}
    except Exception as e:
        print(f"Redis INCR failed: {e}")
        return {"status": "error", "count": 0}

# 4. Corrected Count Getter Route 
@app.get("/count/{hit_id}")
def get_hit_count(hit_id: str):
    try:
        # Retrieve the count value from your Redis instance
        saved_count = r.get(hit_id)
        
        # If the key doesn't exist in Redis yet, return 0 (or fallback gracefully)
        if saved_count is None:
            return 0
            
        # Try converting the stored string to a clean integer
        return int(saved_count)
        
    except Exception as e:
        print(f"Redis GET failed for ID {hit_id}: {e}")
        return 0

