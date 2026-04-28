from functools import wraps
from flask import current_app
import json
import redis

redis_client = None

def init_redis(app):
    global redis_client
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    redis_client = redis.from_url(redis_url, decode_responses=True)

def cache_result(timeout=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return f(*args, **kwargs)
            
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = f(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
