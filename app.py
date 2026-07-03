import os
import redis
from fastapi import FastAPI

app = FastAPI()

# Grab the URL from Render Environment settings
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Use from_url to correctly handle credentials and secure (rediss://) connections
r = redis.from_url(redis_url, decode_responses=True, socket_timeout=3.0)

@app.get("/healthz")
@app.get("/healthz/")
def healthz_check():
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except Exception as e:
        print(f"Health Check Redis failure: {e}")
        return {"status": "ok", "redis": "down"}

@app.post("/hit/{hit_id}")
def handle_dynamic_hit(hit_id: str):
    try:
        # Atomic Redis operation
        new_count = r.incr(hit_id)
        return {
            "status": "success", 
            "count": int(new_count)
        }
    except Exception as e:
        # Crucial: Prints the exact connection error to your Render Logs
        print(f"CRITICAL: Redis INCR failed for ID {hit_id}. Error: {e}")
        
        # Return a visible placeholder so the checker sees a real hint instead of a generic 0
        return {
            "status": "error", 
            "count": -1,
            "details": str(e)
        }
