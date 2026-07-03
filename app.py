import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

app = FastAPI()

# Connect using the service name 'redis' defined in docker-compose
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class CounterResponse(BaseModel):
    key: str
    count: int

class HealthResponse(BaseModel):
    status: str
    redis: str

@app.post("/hit/{key}", response_model=CounterResponse)
def hit_counter(key: str):
    try:
        # Atomic increment via Redis INCR
        new_count = r.incr(key)
        return {"key": key, "count": new_count}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/count/{key}", response_model=CounterResponse)
def get_counter(key: str):
    try:
        val = r.get(key)
        # Default to 0 for unseen keys per requirements
        count = int(val) if val is not None else 0
        return {"key": key, "count": count}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.get("/healthz", response_model=HealthResponse)
def health_check():
    try:
        # Actually ping Redis to ensure live connectivity
        if r.ping():
            return {"status": "ok", "redis": "up"}
        raise ValueError("Ping failed")
    except Exception:
        return {"status": "error", "redis": "down"}
