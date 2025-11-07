# -*- coding: utf-8 -*-
"""
Example of a versioned user API showing evolution from v1 to v3.
"""

from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with
import json


app = Flask(__name__)
api = Api(app, default_version='v1', version_header='Accept')

# Mock user data
users = {
    1: {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'password': 'old_password123'},
    2: {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'password': 'old_password456'},
    3: {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'password': 'old_password789'}
}

# ------------------------------
# Version 1: Basic User API
# ------------------------------
class UserResourceV1(Resource):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String
    }
    
    @marshal_with(user_fields)
    def get(self, user_id):
        if user_id not in users:
            return {'message': 'User not found'}, 404
        return users[user_id]
    
    def delete(self, user_id):
        if user_id not in users:
            return {'message': 'User not found'}, 404
        del users[user_id]
        return {'message': 'User deleted'}, 200

class UserListResourceV1(Resource):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String
    }
    
    @marshal_with(user_fields)
    def get(self):
        return list(users.values())

# ------------------------------
# Version 2: Added password field
# ------------------------------
class UserResourceV2(UserResourceV1):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'password': fields.String
    }
    
    @marshal_with(user_fields)
    def get(self, user_id):
        if user_id not in users:
            return {'message': 'User not found'}, 404
        return users[user_id]

class UserListResourceV2(UserListResourceV1):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'password': fields.String
    }
    
    @marshal_with(user_fields)
    def get(self):
        return list(users.values())

# ------------------------------
# Version 3: Renamed password to secret
# ------------------------------
class UserResourceV3(UserResourceV2):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'secret': fields.String(attribute='password')  # Map password to secret
    }
    
    @marshal_with(user_fields)
    def get(self, user_id):
        if user_id not in users:
            return {'message': 'User not found'}, 404
        return users[user_id]

class UserListResourceV3(UserListResourceV2):
    user_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.String,
        'secret': fields.String(attribute='password')  # Map password to secret
    }
    
    @marshal_with(user_fields)
    def get(self):
        return list(users.values())

# ------------------------------
# Conversion rules
# ------------------------------

def v1_to_v3_request_converter(data):
    """Convert v1 request to v3 format."""
    return data

def v1_to_v3_response_converter(data):
    """Convert v3 response to v1 format."""
    if isinstance(data, list):
        # Handle list of users
        for user in data:
            if 'secret' in user:
                # Remove secret field for v1
                del user['secret']
    elif isinstance(data, dict):
        # Handle single user
        if 'secret' in data:
            del data['secret']
    return data

def v2_to_v3_request_converter(data):
    """Convert v2 request to v3 format."""
    return data

def v2_to_v3_response_converter(data):
    """Convert v3 response to v2 format."""
    if isinstance(data, list):
        # Handle list of users
        for user in data:
            if 'secret' in user:
                # Rename secret to password for v2
                user['password'] = user['secret']
                del user['secret']
    elif isinstance(data, dict):
        # Handle single user
        if 'secret' in data:
            data['password'] = data['secret']
            del data['secret']
    return data

# ------------------------------
# API Configuration
# ------------------------------

# Add versioned resources
api.add_versioned_resource(UserResourceV1, 'v1', '/users/<int:user_id>')
api.add_versioned_resource(UserListResourceV1, 'v1', '/users')

api.add_versioned_resource(UserResourceV2, 'v2', '/users/<int:user_id>')
api.add_versioned_resource(UserListResourceV2, 'v2', '/users')

api.add_versioned_resource(UserResourceV3, 'v3', '/users/<int:user_id>')
api.add_versioned_resource(UserListResourceV3, 'v3', '/users')

# Set version inheritance
api.set_version_inheritance('v2', 'v1')
api.set_version_inheritance('v3', 'v2')

# Deprecate older versions
api.deprecate_version('v1', deprecation_date='2023-01-01', sunset_date='2024-01-01')
api.deprecate_version('v2', deprecation_date='2023-06-01', sunset_date='2024-06-01')

# Add conversion rules
api.add_conversion_rule('v1', 'v3', None, v1_to_v3_response_converter)
api.add_conversion_rule('v2', 'v3', None, v2_to_v3_response_converter)

# ------------------------------
# Test endpoints
# ------------------------------
@app.route('/')
def index():
    return '''
    <h1>Versioned User API Example</h1>
    <p>API versions available: v1, v2, v3</p>
    <p>Example endpoints:</p>
    <ul>
        <li><a href="/v1/users">/v1/users (URL path versioning)</a></li>
        <li><a href="/users?version=2">/users?version=2 (query parameter versioning)</a></li>
        <li><a href="/v3/users/1">/v3/users/1 (URL path versioning)</a></li>
    </ul>
    <p>Use Accept header: "application/json; version=X" for header versioning</p>
    '''

if __name__ == '__main__':
    app.run(debug=True)