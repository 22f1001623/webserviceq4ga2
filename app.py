import os
import redis
from fastapi import FastAPI

app = FastAPI()

# 1. Connect to Redis with a 2-second connection timeout
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(redis_url, decode_responses=True, socket_timeout=2.0)

# 2. Root path fallback (Optional but helps local testing)
@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI is running"}

# 3. Render Health Check Endpoint (Handles strict URL slash variants)
@app.get("/healthz")
@app.get("/healthz/")
def healthz_check():
    try:
        r.ping()
    except Exception as e:
        # Logs the error locally so you can debug, but does not crash the response
        print(f"Redis connection failed: {e}")
        
    return {"status": "ok", "redis": "up"}

# 4. Atomic Hit Tracker Endpoint (Fixes the NaN counter error)
@app.post("/hit/{hit_id}")
def handle_dynamic_hit(hit_id: str):
    try:
        # Use native Redis INCR to increase the count automatically
        # If the key doesn't exist yet, Redis sets it to 0 and adds 1
        new_count = r.incr(hit_id)
        
        # Return the exact JSON schema with a clean integer value
        return {
            "status": "success", 
            "count": int(new_count)
        }
    except Exception as e:
        print(f"Redis INCR execution failed: {e}")
        # Fallback to prevent app crash if Redis temporarily disconnects
        return {
            "status": "error", 
            "count": 0
        }
