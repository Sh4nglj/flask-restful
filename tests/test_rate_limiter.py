import unittest
from flask import Flask, g
from flask_restful import Api, Resource, rate_limit, init_rate_limiter
import redis
import time

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        
        # Enable debug logging
        self.app.logger.setLevel('DEBUG')
        
        # Initialize rate limiter with Redis connection
        init_rate_limiter(self.app, redis_url='redis://localhost:6379/0')
        
        # Whitelist will be set in the whitelist test
        
        # Create test client
        self.client = self.app.test_client()
        
        # Clear Redis data
        r = self.app.extensions['redis']
        r.flushdb()
        
        # Test resource with rate limiting
        class TestResource(Resource):
            method_decorators = [rate_limit(requests=5, window=10, algorithm='token_bucket')]
            def get(self):
                return {'message': 'Success'}
        
        # Add resource to API
        self.api.add_resource(TestResource, '/test')
        
        # Another test resource with sliding window
        class SlidingWindowResource(Resource):
            method_decorators = [rate_limit(requests=3, window=5, algorithm='sliding_window')]
            def get(self):
                return {'message': 'Success'}
        
        self.api.add_resource(SlidingWindowResource, '/sliding')
    
    def test_token_bucket_rate_limit(self):
        # Make 5 requests (should all be allowed)
        for _ in range(5):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get('X-RateLimit-Remaining'), str(4 - _))
        
        # 6th request should be blocked
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)
    
    def test_sliding_window_rate_limit(self):
        # Make 3 requests (should all succeed)
        for i in range(3):
            response = self.client.get('/sliding')
            self.assertEqual(response.status_code, 200)
        
        # 4th request should be rate limited
        response = self.client.get('/sliding')
        self.assertEqual(response.status_code, 429)
    
    def test_whitelist_bypass(self):
        # Set whitelist for this test
        self.app.config['RATE_LIMIT_WHITELIST'] = ['127.0.0.1']
        # Test whitelisted IP (127.0.0.1)
        for i in range(10):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
    
    def test_rate_limit_reset(self):
        # Make 3 requests to reach rate limit
        for _ in range(3):
            self.client.get('/sliding')
        
        # Reset rate limit
        response = self.client.post('/rate-limit/reset', json={'pattern': '*'})
        self.assertEqual(response.status_code, 200)
        
        # Make another request, should be allowed again
        response = self.client.get('/sliding')
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limit_stats(self):
        # Make 3 requests to sliding window endpoint
        for _ in range(3):
            self.client.get('/sliding')
        
        # Get rate limit stats
        response = self.client.get('/rate-limit/stats')
        self.assertEqual(response.status_code, 200)
        
        stats = response.get_json()
        print(f'Stats: {stats}')
        
        # Check if stats are correctly calculated
        self.assertIsInstance(stats, list)
        test_stats = next((s for s in stats if s['endpoint'] == 'slidingwindowresource'), None)
        self.assertIsNotNone(test_stats)
        self.assertEqual(test_stats['requests'], 3)
        self.assertEqual(test_stats['limited'], 0)
        self.assertEqual(test_stats['algorithm'], 'sliding_window')
        self.assertGreater(test_stats['avg_response_time'], 0)

    def test_dynamic_rate_limit(self):
        # Get Redis instance
        r = self.app.extensions['redis']
        
        # Set dynamic configuration for test endpoint
        r.hset('dynamic_rate_limit:testresource', mapping={
            'requests': 2,
            'window': 10,
            'algorithm': 'fixed_window'
        })
        
        # Make 2 requests (should all succeed)
        for i in range(2):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
        
        # 3rd request should be rate limited
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)
        
        # Test global dynamic configuration
        r.flushdb()
        r.hset('dynamic_rate_limit:global', mapping={
            'requests': 1,
            'window': 10,
            'algorithm': 'leaky_bucket'
        })
        
        # Make 1 request (should succeed)
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 200)
        
        # 2nd request should be rate limited
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)

    def test_multi_dimension_key(self):
        # Add a test resource with combined key
        class MultiDimensionResource(Resource):
            method_decorators = [rate_limit(
                requests=2, 
                window=10, 
                key_func=lambda: f'{request.remote_addr}_{g.get("user_id", "anonymous")}'
            )]
            def get(self):
                return {'message': 'Success'}
        
        self.api.add_resource(MultiDimensionResource, '/multi')
        
        # First user
        def set_user1():
            g.user_id = 'user1'
        
        self.app.before_request(set_user1)
        
        # Make 2 requests (should succeed)
        for i in range(2):
            response = self.client.get('/multi')
            self.assertEqual(response.status_code, 200)
        
        # 3rd request should be rate limited
        response = self.client.get('/multi')
        self.assertEqual(response.status_code, 429)
        
        # Remove the before_request handler
        self.app.before_request_funcs[None].remove(set_user1)
        
        # Second user (should not be limited)
        def set_user2():
            g.user_id = 'user2'
        
        self.app.before_request(set_user2)
        
        # Make 1 request (should succeed)
        response = self.client.get('/multi')
        self.assertEqual(response.status_code, 200)
        
        # Remove the before_request handler
        self.app.before_request_funcs[None].remove(set_user2)

if __name__ == '__main__':
    unittest.main()