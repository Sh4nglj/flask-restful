import time
import functools
from flask import request, g
import threading
import pickle

# Try to import Redis, if not available, RedisStorage will raise an error when used
try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False

class BaseStorage:
    def __init__(self):
        pass
    def get(self, key):
        raise NotImplementedError
    def set(self, key, value, expire=None):
        raise NotImplementedError
    def incr(self, key, expire=None):
        raise NotImplementedError
    def delete(self, key):
        raise NotImplementedError

class MemoryStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.storage = {}
        self.expire_times = {}
        self.lock = threading.Lock()
    def get(self, key):
        with self.lock:
            if key in self.storage:
                # Check if the key has expired
                if key in self.expire_times:
                    if time.time() > self.expire_times[key]:
                        del self.storage[key]
                        del self.expire_times[key]
                        return None
                return self.storage[key]
            return None
    def set(self, key, value, expire=None):
        with self.lock:
            self.storage[key] = value
            if expire is not None:
                self.expire_times[key] = time.time() + expire
            elif key in self.expire_times:
                del self.expire_times[key]
    def incr(self, key, expire=None):
        with self.lock:
            value = self.get(key)
            if value is None:
                value = 0
            new_value = value + 1
            self.set(key, new_value, expire)
            return new_value
    def delete(self, key):
        with self.lock:
            if key in self.storage:
                del self.storage[key]
            if key in self.expire_times:
                del self.expire_times[key]

class TokenBucket:
    def __init__(self, rps, burst, storage, key_func):
        self.rps = rps
        self.burst = burst
        self.storage = storage
        self.key_func = key_func
    def get_token(self):
        key = self.key_func()
        bucket = self.storage.get(key)
        now = time.time()
        if not bucket:
            bucket = {
                'tokens': self.burst,
                'last_refill': now
            }
            self.storage.set(key, bucket)
        else:
            tokens_to_add = (now - bucket['last_refill']) * self.rps
            bucket['tokens'] = min(self.burst, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            self.storage.set(key, bucket)
            return True
        return False

class RedisStorage(BaseStorage):
    def __init__(self, host='localhost', port=6379, db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None, socket_keepalive=None, socket_keepalive_options=None,
                 max_connections=None, encoding='utf-8', encoding_errors='strict', decode_responses=False,
                 retry_on_timeout=False, ssl=False, ssl_keyfile=None, ssl_certfile=None, ssl_cert_reqs=None,
                 ssl_ca_certs=None, ssl_ca_path=None, ssl_ca_data=None):
        super().__init__()
        if not redis_available:
            raise ImportError("Redis is not installed. Please install it with 'pip install redis'.")
        self.redis = redis.Redis(host=host, port=port, db=db, password=password, socket_timeout=socket_timeout,
                                 socket_connect_timeout=socket_connect_timeout, socket_keepalive=socket_keepalive,
                                 socket_keepalive_options=socket_keepalive_options, max_connections=max_connections,
                                 encoding=encoding, encoding_errors=encoding_errors, decode_responses=decode_responses,
                                 retry_on_timeout=retry_on_timeout, ssl=ssl, ssl_keyfile=ssl_keyfile,
                                 ssl_certfile=ssl_certfile, ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                                 ssl_ca_path=ssl_ca_path, ssl_ca_data=ssl_ca_data)
    def get(self, key):
        try:
            value = self.redis.get(key)
            return pickle.loads(value) if value is not None else None
        except redis.RedisError:
            return None
    def set(self, key, value, expire=None):
        try:
            pickled_value = pickle.dumps(value)
            if expire is not None:
                self.redis.setex(key, int(expire), pickled_value)
            else:
                self.redis.set(key, pickled_value)
        except redis.RedisError:
            pass
    def incr(self, key, expire=None):
        try:
            if expire is not None:
                # Redis incr doesn't support expire parameter for existing keys
                # So we need to handle it specially
                with self.redis.pipeline() as pipe:
                    pipe.incr(key)
                    pipe.expire(key, int(expire))
                    return pipe.execute()[0]
            else:
                return self.redis.incr(key)
        except redis.RedisError:
            return None
    def delete(self, key):
        try:
            self.redis.delete(key)
        except redis.RedisError:
            pass

class SlidingWindow:
    def __init__(self, rps, burst, storage, key_func):
        self.rps = rps
        self.burst = burst
        self.storage = storage
        self.key_func = key_func
    def get_token(self):
        key = self.key_func()
        window = self.storage.get(key)
        now = time.time()
        if not window:
            window = []
        # Filter requests within the time window (1 second)
        window = [t for t in window if now - t < 1]
        # Check if we're within both rps and burst limits
        if len(window) < self.rps and len(window) < self.burst:
            window.append(now)
            self.storage.set(key, window)
            return True
        return False

def get_ip_key_func():
    def key_func():
        return request.remote_addr
    return key_func

def get_user_key_func():
    def key_func():
        return g.get('user_id', request.remote_addr)
    return key_func

class RateLimiter:
    def __init__(self, rps=100, burst=200, key_func=get_ip_key_func(), storage=MemoryStorage(), strategy='token_bucket', whitelist=None, enable_stats=True):
        self.rps = rps
        self.burst = burst
        self.key_func = key_func
        self.storage = storage
        self.strategy = strategy
        self.whitelist = whitelist or []
        self.enable_stats = enable_stats
        if strategy == 'token_bucket':
            self.limiter = TokenBucket(rps, burst, storage, key_func)
        elif strategy == 'sliding_window':
            self.limiter = SlidingWindow(rps, burst, storage, key_func)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    def __call__(self, func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            key = self.key_func()
            if key in self.whitelist:
                return func(*args, **kwargs)
            if not self.limiter.get_token():
                # Calculate retry after time (minimum 1 second)
                retry_after = max(1, int(1 / self.rps))
                if self.enable_stats:
                    # Increment total限流 count
                    self.storage.incr(f'rate_limit:count:{key}')
                    # Increment per-minute count
                    now = time.time()
                    minute_key = f'rate_limit:count:{key}:{int(now // 60)}'
                    self.storage.incr(minute_key, expire=60)
                    # Increment per-hour count
                    hour_key = f'rate_limit:count:{key}:{int(now // 3600)}'
                    self.storage.incr(hour_key, expire=3600)
                return {'message': 'Too Many Requests'}, 429, {'Retry-After': str(retry_after)}
            return func(*args, **kwargs)
        return decorated
    def get_stats(self, key):
        """Get rate limit stats for the given key"""
        total = self.storage.get(f'rate_limit:count:{key}')
        # Get current minute stats
        now = time.time()
        minute_key = f'rate_limit:count:{key}:{int(now // 60)}'
        minute = self.storage.get(minute_key)
        # Get current hour stats
        hour_key = f'rate_limit:count:{key}:{int(now // 3600)}'
        hour = self.storage.get(hour_key)
        return {
            'total': total or 0,
            'per_minute': minute or 0,
            'per_hour': hour or 0
        }
    def reset_stats(self, key):
        """Reset rate limit stats for the given key"""
        self.storage.delete(f'rate_limit:count:{key}')
        now = time.time()
        minute_key = f'rate_limit:count:{key}:{int(now // 60)}'
        self.storage.delete(minute_key)
        hour_key = f'rate_limit:count:{key}:{int(now // 3600)}'
        self.storage.delete(hour_key)

rate_limit = RateLimiter

def configure_global_rate_limit(rps=100, burst=200, storage=MemoryStorage(), strategy='token_bucket', whitelist=None):
    """
    Create a global rate limit decorator that can be used with Flask-RESTful Api.decorators
    
    Example:
        from flask_restful import Api
        from flask_restful.utils.rate_limit import configure_global_rate_limit
        
        api = Api(app, decorators=[configure_global_rate_limit(rps=100, burst=200)])
        
    This will apply the rate limit to all resources managed by the API
    """
    return RateLimiter(rps=rps, burst=burst, storage=storage, strategy=strategy, whitelist=whitelist)