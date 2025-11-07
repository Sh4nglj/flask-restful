# -*- coding: utf-8 -*-
"""
Tests for API version control functionality.
"""

import unittest
import json
from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with


class TestAPIVersioning(unittest.TestCase):
    """Test API versioning functionality."""
    
    def setUp(self):
        """Set up test app and API."""
        self.app = Flask(__name__)
        self.api = Api(self.app, default_version='v1', version_header='X-API-Version', version_query_param='version')
        
        # Mock data
        self.users = {
            1: {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            2: {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
        }
        
        # Create a closure to capture the users data
        users = self.users
        
        # Version 1 resources
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
        
        class UserListResourceV1(Resource):
            user_fields = {
                'id': fields.Integer,
                'name': fields.String,
                'email': fields.String
            }
            
            @marshal_with(user_fields)
            def get(self):
                return list(users.values())
        
        # Version 2 resources (added password field)
        class UserResourceV2(UserResourceV1):
            user_fields = {
                'id': fields.Integer,
                'name': fields.String,
                'email': fields.String,
                'password': fields.String(default='secret')
            }
            
            @marshal_with(user_fields)
            def get(self, user_id):
                if user_id not in users:
                    return {'message': 'User not found'}, 404
                user = users[user_id].copy()
                user['password'] = 'secret'
                return user
        
        class UserListResourceV2(UserListResourceV1):
            user_fields = {
                'id': fields.Integer,
                'name': fields.String,
                'email': fields.String,
                'password': fields.String(default='secret')
            }
            
            @marshal_with(user_fields)
            def get(self):
                users_with_password = []
                for user in users.values():
                    user_copy = user.copy()
                    user_copy['password'] = 'secret'
                    users_with_password.append(user_copy)
                return users_with_password
        
        # Add resources
        self.api.add_versioned_resource(UserResourceV1, 'v1', '/users/<int:user_id>')
        self.api.add_versioned_resource(UserListResourceV1, 'v1', '/users')
        self.api.add_versioned_resource(UserResourceV2, 'v2', '/users/<int:user_id>')
        self.api.add_versioned_resource(UserListResourceV2, 'v2', '/users')
        
        # Set up version inheritance
        self.api.set_version_inheritance('v2', 'v1')
        
        # Deprecate version 1
        self.api.deprecate_version('v1', deprecation_date='2023-01-01', sunset_date='2024-01-01')
        
        self.client = self.app.test_client()
    
    def test_url_path_versioning(self):
        """Test versioning via URL path."""
        # Test v1
        response = self.client.get('/v1/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('email', data[0])
        self.assertNotIn('password', data[0])
        
        # Test v2
        response = self.client.get('/v2/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('email', data[0])
        self.assertIn('password', data[0])
    
    def test_query_param_versioning(self):
        """Test versioning via query parameter."""
        # Test v1
        response = self.client.get('/users?version=v1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('password', data[0])
        
        # Test v2
        response = self.client.get('/users?version=v2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('password', data[0])
    
    def test_header_versioning(self):
        """Test versioning via request header."""
        # Test v1
        response = self.client.get('/users', headers={'Accept': 'application/json; version=v1'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('password', data[0])
        
        # Test v2
        response = self.client.get('/users', headers={'Accept': 'application/json; version=v2'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('password', data[0])
    
    def test_default_version(self):
        """Test default version functionality."""
        response = self.client.get('/users')  # Should use default version v1
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertNotIn('password', data[0])
    
    def test_deprecation_headers(self):
        """Test that deprecated versions return warning headers."""
        response = self.client.get('/v1/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Deprecation', response.headers)
        self.assertIn('Sunset', response.headers)
        self.assertIn('Link', response.headers)
    
    def test_version_inheritance(self):
        """Test version inheritance."""
        # This test ensures that version inheritance is properly recorded
        self.assertIn('v2', self.api.version_inheritance)
        self.assertEqual(self.api.version_inheritance['v2'], 'v1')
    
    def test_version_deprecation(self):
        """Test version deprecation status."""
        self.assertTrue(self.api.is_version_deprecated('v1'))
        self.assertFalse(self.api.is_version_deprecated('v2'))
        
        deprecation_date, sunset_date = self.api.get_deprecation_info('v1')
        self.assertEqual(deprecation_date, '2023-01-01')
        self.assertEqual(sunset_date, '2024-01-01')
    
    def test_single_user_endpoint(self):
        """Test single user endpoint across versions."""
        # Test v1
        response = self.client.get('/v1/users/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'John Doe')
        self.assertNotIn('password', data)
        
        # Test v2
        response = self.client.get('/v2/users/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'John Doe')
        self.assertIn('password', data)
        self.assertEqual(data['password'], 'secret')


class TestAPIConversionRules(unittest.TestCase):
    """Test API request/response conversion rules."""
    
    def setUp(self):
        """Set up test app and API with conversion rules."""
        self.app = Flask(__name__)
        self.api = Api(self.app, default_version='v3', version_header='X-API-Version', version_query_param='version')
        
        # Mock data
        self.users = {
            1: {'id': 1, 'name': 'John Doe', 'secret': 'mysecretpassword'}
        }
        
        # Create a closure to capture the users data
        users = self.users
        
        # Version 3 resource (uses 'secret' instead of 'password')
        class UserResourceV3(Resource):
            user_fields = {
                'id': fields.Integer,
                'name': fields.String,
                'secret': fields.String
            }
            
            @marshal_with(user_fields)
            def get(self, user_id):
                if user_id not in users:
                    return {'message': 'User not found'}, 404
                return users[user_id]
        
        class UserListResourceV3(Resource):
            user_fields = {
                'id': fields.Integer,
                'name': fields.String,
                'secret': fields.String
            }
            
            @marshal_with(user_fields)
            def get(self):
                return list(users.values())
        
        # Add v3 as the only resource (latest version)
        self.api.add_versioned_resource(UserResourceV3, 'v3', '/users/<int:user_id>')
        self.api.add_versioned_resource(UserListResourceV3, 'v3', '/users')
        
        # Conversion rules
        def v1_to_v3_response_converter(data):
            """Convert v3 response to v1 format (remove secret)."""
            if isinstance(data, list):
                for user in data:
                    if 'secret' in user:
                        del user['secret']
            elif isinstance(data, dict):
                if 'secret' in data:
                    del data['secret']
            return data
        
        def v2_to_v3_response_converter(data):
            """Convert v3 response to v2 format (rename secret to password)."""
            if isinstance(data, list):
                for user in data:
                    if 'secret' in user:
                        user['password'] = user['secret']
                        del user['secret']
            elif isinstance(data, dict):
                if 'secret' in data:
                    data['password'] = data['secret']
                    del data['secret']
            return data
        
        self.api.add_conversion_rule('v1', 'v3', None, v1_to_v3_response_converter)
        self.api.add_conversion_rule('v2', 'v3', None, v2_to_v3_response_converter)
        
        self.client = self.app.test_client()
    
    def test_response_conversion_v1(self):
        """Test response conversion from v3 to v1."""
        # Test with header versioning
        response = self.client.get('/users', headers={'Accept': 'application/json; version=v1'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertNotIn('secret', data[0])
        self.assertNotIn('password', data[0])
    
    def test_response_conversion_v2(self):
        """Test response conversion from v3 to v2."""
        # Test with query parameter versioning
        response = self.client.get('/users?version=v2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('password', data[0])  # Should have password, not secret
        self.assertNotIn('secret', data[0])
    
    def test_no_conversion_needed(self):
        """Test that no conversion is done for the latest version."""
        response = self.client.get('/v3/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('id', data[0])
        self.assertIn('name', data[0])
        self.assertIn('secret', data[0])  # Should have secret, not password


if __name__ == '__main__':
    unittest.main()