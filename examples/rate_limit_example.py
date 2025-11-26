from flask import Flask, g
from flask_restful import Api, Resource, rate_limit, init_rate_limiter, ip_key, user_id_key, combined_key
import redis

app = Flask(__name__)
api = Api(app)

# Initialize rate limiter with Redis connection
init_rate_limiter(app, redis_url='redis://localhost:6379/0')

# Set rate limit whitelist
app.config['RATE_LIMIT_WHITELIST'] = ['127.0.0.1']

# Example middleware to simulate authenticated user
@app.before_request
def set_user_context():
    # In a real application, this would come from authentication
    g.user_id = 'user_123'
    g.user_role = 'user'

# Example resource with rate limiting
@rate_limit(requests=10, window=60, algorithm='token_bucket', key_func=lambda: combined_key(ip_key, user_id_key))
class ProtectedResource(Resource):
    def get(self):
        return {
            'message': 'This is a protected resource',
            'user_id': g.user_id,
            'ip': g.request.remote_addr
        }

# Another example resource with different rate limit
@rate_limit(requests=5, window=60, algorithm='sliding_window', key_func=ip_key)
class PublicResource(Resource):
    def get(self):
        return {
            'message': 'This is a public resource',
            'ip': g.request.remote_addr
        }

# Add resources to API
api.add_resource(ProtectedResource, '/protected')
api.add_resource(PublicResource, '/public')

if __name__ == '__main__':
    app.run(debug=True)