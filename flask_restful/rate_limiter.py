from __future__ import absolute_import
import time
import redis
from functools import wraps
from flask import request, g, current_app, make_response
import threading
import random

# 限流算法实现
class RateLimitAlgorithm:
    def __init__(self, requests, window):
        self.requests = requests
        self.window = window

    def allow_request(self, key):
        raise NotImplementedError

    def get_remaining(self, key):
        raise NotImplementedError

    def get_reset_time(self, key):
        raise NotImplementedError


class TokenBucket(RateLimitAlgorithm):
    def __init__(self, requests, window):
        super().__init__(requests, window)
        self.rate = requests / window  # 每秒发放令牌数
        self.capacity = requests  # 令牌桶容量

    def allow_request(self, key):
        # 使用Redis存储令牌桶状态
        r = current_app.extensions.get('redis', None)
        if not r:
            return True, self.get_remaining(key), self.get_reset_time(key)

        pipeline = r.pipeline()
        pipeline.hgetall(f'token_bucket:{key}')
        pipeline.time()
        result = pipeline.execute()

        current_time = result[1][0] + result[1][1] / 1e6
        bucket = result[0]

        tokens = float(bucket.get(b'tokens', self.capacity))
        last_refill_time = float(bucket.get(b'last_refill_time', current_time))

        # 计算需要补充的令牌数量
        tokens_to_add = (current_time - last_refill_time) * self.rate
        if tokens_to_add > 0:
            tokens = min(tokens + tokens_to_add, self.capacity)
            last_refill_time = current_time

        allowed = False
        if tokens >= 1:
            tokens -= 1
            allowed = True

        # 更新令牌桶状态
        pipeline.hset(f'token_bucket:{key}', mapping={
            'tokens': tokens,
            'last_refill_time': last_refill_time
        })
        pipeline.expire(f'token_bucket:{key}', self.window)
        pipeline.execute()

        return allowed, tokens, int(last_refill_time + self.window)


class LeakyBucket(RateLimitAlgorithm):
    def __init__(self, requests, window):
        super().__init__(requests, window)
        self.rate = requests / window  # 每秒流出速率
        self.capacity = requests  # 漏桶容量

    def allow_request(self, key):
        # 使用Redis存储漏桶状态
        r = current_app.extensions.get('redis', None)
        if not r:
            return True, self.get_remaining(key), self.get_reset_time(key)

        pipeline = r.pipeline()
        pipeline.hgetall(f'leaky_bucket:{key}')
        pipeline.time()
        result = pipeline.execute()

        current_time = result[1][0] + result[1][1] / 1e6
        bucket = result[0]

        # 计算当前桶中的请求数量
        requests_in_bucket = float(bucket.get(b'requests', 0))
        last_leak_time = float(bucket.get(b'last_leak_time', current_time))

        # 计算漏出的请求数量
        requests_leaked = (current_time - last_leak_time) * self.rate
        if requests_leaked > 0:
            requests_in_bucket = max(requests_in_bucket - requests_leaked, 0)
            last_leak_time = current_time

        allowed = False
        if requests_in_bucket < self.capacity:  # 使用动态设置的容量
            allowed = True
            requests_in_bucket += 1

        # 更新漏桶状态
        pipeline.hset(f'leaky_bucket:{key}', mapping={
            'requests': requests_in_bucket,
            'last_leak_time': last_leak_time
        })
        pipeline.expire(f'leaky_bucket:{key}', self.window)
        pipeline.execute()

        return allowed, 1 - requests_in_bucket, int(last_leak_time + self.window)


class FixedWindow(RateLimitAlgorithm):
    def __init__(self, requests, window):
        super().__init__(requests, window)

    def allow_request(self, key):
        # 使用Redis存储固定窗口状态
        r = current_app.extensions.get('redis', None)
        if not r:
            return True, self.get_remaining(key), self.get_reset_time(key)

        current_time = int(time.time())
        window_start = current_time - (current_time % self.window)
        window_end = window_start + self.window

        key_name = f'fixed_window:{key}:{window_start}'
        count = r.incr(key_name)

        if count == 1:
            r.expire(key_name, self.window)

        allowed = count <= self.requests
        remaining = max(self.requests - count, 0)

        return allowed, remaining, window_end


class SlidingWindow(RateLimitAlgorithm):
    def __init__(self, requests, window):
        super().__init__(requests, window)
        self.granularity = 1  # 滑动窗口粒度，秒

    def allow_request(self, key):
        # 使用Redis存储滑动窗口状态
        r = current_app.extensions.get('redis', None)
        if not r:
            return True, self.get_remaining(key), self.get_reset_time(key)

        current_time = int(time.time())
        window_end = current_time
        window_start = window_end - self.window

        pipeline = r.pipeline()
        # 删除过期的时间桶
        pipeline.zremrangebyscore(f'sliding_window:{key}', 0, window_start - 1)
        # 获取当前窗口内的请求总数
        pipeline.zcard(f'sliding_window:{key}')
        # 向有序集合中添加当前请求
        pipeline.zadd(f'sliding_window:{key}', {current_time: current_time})
        # 设置有序集合的过期时间
        pipeline.expire(f'sliding_window:{key}', self.window)
        result = pipeline.execute()

        count = result[1] + 1  # 加上当前请求
        allowed = count <= self.requests
        remaining = max(self.requests - count, 0)

        return allowed, remaining, window_end + self.window


# 限流装饰器
def rate_limit(requests=100, window=60, algorithm='token_bucket', key_func=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取限流键
            if key_func:
                key = key_func()
            else:
                # 默认基于IP地址限流
                key = request.remote_addr

            # 检查白名单
            whitelist = current_app.config.get('RATE_LIMIT_WHITELIST', [])
            if key in whitelist:
                return func(*args, **kwargs)

            # 从Redis获取动态限流配置
            r = current_app.extensions.get('redis', None)
            dynamic_config = None
            if r:
                # 尝试获取更细粒度的配置（按端点）
                endpoint = request.endpoint or 'unknown'
                dynamic_config = r.hgetall(f'dynamic_rate_limit:{endpoint}')
                if not dynamic_config:
                    # 尝试获取全局动态配置
                    dynamic_config = r.hgetall('dynamic_rate_limit:global')

            # 应用动态配置
            # 使用默认值初始化限流参数
            current_requests = requests
            current_window = window
            current_algorithm = algorithm
            
            if dynamic_config:
                try:
                    current_requests = int(dynamic_config.get(b'requests', current_requests))
                    current_window = int(dynamic_config.get(b'window', current_window))
                    current_algorithm = dynamic_config.get(b'algorithm', current_algorithm).decode('utf-8')
                except (ValueError, TypeError):
                    # 如果动态配置无效，使用默认值
                    pass

            # 选择限流算法
            algorithms = {
                'token_bucket': TokenBucket,
                'leaky_bucket': LeakyBucket,
                'fixed_window': FixedWindow,
                'sliding_window': SlidingWindow
            }
            if current_algorithm not in algorithms:
                return func(*args, **kwargs)

            rate_limiter = algorithms[current_algorithm](current_requests, current_window)
            allowed, remaining, reset_time = rate_limiter.allow_request(key)

            # 更新统计信息
            if 'rate_limit_stats' not in g:
                g.rate_limit_stats = {}
            g.rate_limit_stats.update({
                'requests': current_requests,
                'remaining': remaining,
                'reset': reset_time,
                'algorithm': current_algorithm
            })

            # Set rate limit headers regardless of whether the request is allowed
            headers = {
                'X-RateLimit-Limit': str(current_requests),
                'X-RateLimit-Remaining': str(round(remaining)),
                'X-RateLimit-Reset': str(reset_time)
            }
            if not allowed:
                # Return 429 Too Many Requests
                headers['Retry-After'] = str(reset_time - int(time.time()))
                response = make_response({
                    'message': 'Too Many Requests',
                    'error': 'Rate limit exceeded'
                }, 429)
                response.headers.extend(headers)
                return response

            # Add headers to allowed response
            response = func(*args, **kwargs)
            if isinstance(response, tuple) and len(response) == 2:
                data, status_code = response
                response = make_response(data, status_code)
            elif isinstance(response, dict):
                response = make_response(response)
            response.headers.extend(headers)
            return response
        return wrapper
    return decorator


# 多维度限流键生成函数
def ip_key():
    return request.remote_addr

def user_id_key():
    return g.get('user_id', 'anonymous')

def api_endpoint_key():
    return request.endpoint

def user_role_key():
    return g.get('user_role', 'guest')


def combined_key(*key_functions):
    def _combined_key():
        return '_'.join([func() for func in key_functions])
    return _combined_key


# 动态限流调整
class DynamicRateLimitAdjuster:
    def __init__(self, redis_instance, app=None):
        self.redis = redis_instance
        self.app = app
        # Only start the adjuster if dynamic rate limiting is enabled
        if app and app.config.get('DYNAMIC_RATE_LIMIT_ENABLED', False):
            self.thread = threading.Thread(target=self._adjust_loop, daemon=True)
            self.thread.start()

    def _adjust_loop(self):
        while True:
            # 这里可以添加服务器负载监控逻辑，根据负载调整限流阈值
            # 示例：随机调整（实际应用中应根据真实负载数据）
            load = random.uniform(0.1, 0.9)
            new_requests = int(100 * (1 - load)) + 10
            # 使用哈希结构存储动态配置，支持requests、window、algorithm
            self.redis.hset('dynamic_rate_limit:global', mapping={
                'requests': new_requests,
                'window': 60,
                'algorithm': 'token_bucket'
            })
            time.sleep(60)  # 每分钟调整一次




# 初始化函数
def init_rate_limiter(app, redis_url='redis://localhost:6379/0'):
    # 管理API需要在初始化时导入，避免循环导入
    from flask_restful import Resource, fields, marshal_with
    
    global stats_fields, RateLimitStatsResource, RateLimitConfigResource, RateLimitResetResource
    
    stats_fields = {
        'endpoint': fields.String,
        'requests': fields.Integer,
        'limited': fields.Integer,
        'avg_response_time': fields.Float,
        'algorithm': fields.String
    }

    class RateLimitStatsResource(Resource):
        @marshal_with(stats_fields)
        def get(self):
            # 获取限流统计信息
            r = current_app.extensions.get('redis', None)
            if not r:
                return []

            stats = []
            for key in r.keys('rate_limit_stats:*'):
                stats_key = key.decode('utf-8')
                endpoint = stats_key.split(':')[1]
                data = r.hgetall(key)
                stats.append({
                    'endpoint': endpoint,
                    'requests': int(data.get(b'requests', 0)),
                    'limited': int(data.get(b'limited', 0)),
                    'avg_response_time': float(data.get(b'avg_response_time', 0)),
                    'algorithm': data.get(b'algorithm', b'').decode('utf-8')
                })
            return stats


    class RateLimitConfigResource(Resource):
        def get(self):
            # 获取限流配置
            config = {
                'default_requests': current_app.config.get('RATE_LIMIT_DEFAULT_REQUESTS', 100),
                'default_window': current_app.config.get('RATE_LIMIT_DEFAULT_WINDOW', 60),
                'default_algorithm': current_app.config.get('RATE_LIMIT_DEFAULT_ALGORITHM', 'token_bucket'),
                'whitelist': current_app.config.get('RATE_LIMIT_WHITELIST', [])
            }
            return config

        def put(self):
            # 更新限流配置
            data = request.get_json()
            if 'default_requests' in data:
                current_app.config['RATE_LIMIT_DEFAULT_REQUESTS'] = data['default_requests']
            if 'default_window' in data:
                current_app.config['RATE_LIMIT_DEFAULT_WINDOW'] = data['default_window']
            if 'default_algorithm' in data:
                current_app.config['RATE_LIMIT_DEFAULT_ALGORITHM'] = data['default_algorithm']
            if 'whitelist' in data:
                current_app.config['RATE_LIMIT_WHITELIST'] = data['whitelist']
            return {'message': 'Rate limit configuration updated successfully'}


    class RateLimitResetResource(Resource):
        def post(self):
            # 重置限流计数
            r = current_app.extensions.get('redis', None)
            if not r:
                return {'message': 'No Redis connection available'}

            pattern = request.args.get('pattern', '*')
            # 匹配所有限流相关的键格式
            key_patterns = [
                f'token_bucket:{pattern}',
                f'leaky_bucket:{pattern}',
                f'fixed_window:{pattern}:*',
                f'sliding_window:{pattern}'
            ]
            
            keys = []
            for key_pattern in key_patterns:
                keys.extend(r.keys(key_pattern))
                
            if keys:
                r.delete(*keys)
            return {'message': f'Reset {len(keys)} rate limit keys'}
    
    # 初始化Redis连接
    r = redis.from_url(redis_url)
    app.extensions['redis'] = r

    # 初始化动态限流调整器
    DynamicRateLimitAdjuster(r, app)

    # 添加管理API端点
    api = app.extensions.get('restful_api', None)
    if api:
        # Check if endpoints already exist before adding
        if 'ratelimitstatsresource' not in api.endpoints:
            api.add_resource(RateLimitStatsResource, '/rate-limit/stats')
        if 'ratelimitconfigresource' not in api.endpoints:
            api.add_resource(RateLimitConfigResource, '/rate-limit/config')
        if 'ratelimitresetresource' not in api.endpoints:
            api.add_resource(RateLimitResetResource, '/rate-limit/reset')

    # 添加请求前处理函数，记录请求开始时间
    @app.before_request
    def record_request_start_time():
        g.request_start_time = time.time()

    # 添加请求后处理函数，记录响应时间
    @app.after_request
    def record_response_time(response):
        if hasattr(g, 'request_start_time'):
            g.response_time = time.time() - g.request_start_time
        return response

    # 添加请求后处理函数，记录统计信息（确保在记录响应时间之后执行）
    @app.after_request
    def record_rate_limit_stats(response):
        if hasattr(g, 'rate_limit_stats'):
            r = current_app.extensions.get('redis', None)
            if r:
                endpoint = request.endpoint or 'unknown'
                stats_key = f'rate_limit_stats:{endpoint}'
                pipeline = r.pipeline()
                
                # 增加总请求数
                pipeline.hincrby(stats_key, 'requests', 1)
                
                # 如果响应状态码是429，增加被限流次数
                limited = 1 if response.status_code == 429 else 0
                pipeline.hincrby(stats_key, 'limited', limited)
                
                pipeline.hset(stats_key, 'algorithm', g.rate_limit_stats['algorithm'])
                
                # 计算平均响应时间
                response_time = getattr(g, 'response_time', 0)
                current_avg = float(r.hget(stats_key, 'avg_response_time') or 0)
                count = int(r.hget(stats_key, 'requests') or 1)
                new_avg = (current_avg * (count - 1) + response_time) / count
                pipeline.hset(stats_key, 'avg_response_time', new_avg)
                
                pipeline.execute()
        return response