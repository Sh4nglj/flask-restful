import unittest
import json
import time
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
import flask_restful
from flask_restful import Api, Resource, abort
from flask_restful.auth import Auth, TokenBlacklist, require_auth, require_role, users, token_blacklist, login_attempts, generate_token


class ProtectedResource(Resource):
    @require_auth
    def get(self):
        return {'message': 'This is a protected resource'}


class AdminResource(Resource):
    @require_auth
    @require_role('admin')
    def get(self):
        return {'message': 'This is an admin-only resource'}


class EditorResource(Resource):
    @require_auth
    @require_role('editor')
    def get(self):
        return {'message': 'This is an editor-only resource'}


class ViewerResource(Resource):
    @require_auth
    @require_role('viewer')
    def get(self):
        return {'message': 'This is a viewer-only resource'}


class AuthTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.api = Api(self.app)
        
        # Add authentication endpoints
        self.api.add_resource(Auth, '/auth/<string:endpoint>')
        
        # Add protected resources
        self.api.add_resource(ProtectedResource, '/protected')
        self.api.add_resource(AdminResource, '/admin')
        self.api.add_resource(EditorResource, '/editor')
        self.api.add_resource(ViewerResource, '/viewer')
        
        # Clear in-memory storage
        users.clear()
        token_blacklist.clear()
        login_attempts.clear()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        # Clear in-memory storage
        users.clear()
        token_blacklist.clear()
        login_attempts.clear()
    
    def test_user_registration(self):
        response = self.client.post(
            '/auth/register',
            json={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com', 'roles': ['editor', 'viewer']}
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')
        
        # Check if user exists
        self.assertIn('testuser', users)
        self.assertEqual(users['testuser']['email'], 'test@example.com')
        self.assertEqual(users['testuser']['roles'], ['editor', 'viewer'])
    
    def test_user_registration_duplicate_username(self):
        # First registration
        self.client.post(
            '/auth/register',
            json={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Second registration with same username
        response = self.client.post(
            '/auth/register',
            json={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test2@example.com'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Username already exists')
    
    def test_user_registration_weak_password(self):
        # Test password too short
        response = self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': '1234', 
                  'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('must be at least', data['message'])
        
        # Test password without uppercase
        response = self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'testpass123!', 
                  'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('uppercase', data['message'])
        
        # Test password without lowercase
        response = self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TESTPASS123!', 
                  'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('lowercase', data['message'])
        
        # Test password without digit
        response = self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass!', 
                  'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('digit', data['message'])
        
        # Test password without special character
        response = self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123', 
                  'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('special', data['message'])
    
    def test_user_login(self):
        # Register user first
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Test login
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'TestPass123!'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertEqual(data['token_type'], 'Bearer')
        self.assertEqual(data['expires_in'], 3600)
    
    def test_user_login_invalid_password(self):
        # Register user first
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Test login with invalid password
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'WrongPass!123'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid username or password')
    
    def test_user_login_nonexistent_user(self):
        # Test login with non-existent user
        response = self.client.post(
            '/auth/login',
            data={'username': 'nonexistent', 'password': 'TestPass123!'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid username or password')
    
    def test_user_login_account_lock(self):
        # Register user first
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Attempt login 5 times with invalid password
        for i in range(5):
            response = self.client.post(
                '/auth/login',
                data={'username': 'testuser', 'password': 'WrongPass!123'}
            )
            self.assertEqual(response.status_code, 401)
        
        # 6th attempt should lock account
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'TestPass123!'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Account is locked', data['message'])
    
    def test_access_protected_resource(self):
        # Register user first
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Login to get token
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'TestPass123!'}
        )
        data = json.loads(response.data)
        access_token = data['access_token']
        
        # Access protected resource
        response = self.client.get(
            '/protected',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'This is a protected resource')
    
    def test_access_protected_resource_no_token(self):
        # Access protected resource without token
        response = self.client.get('/protected')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Authorization header is missing')
    
    def test_access_protected_resource_invalid_token(self):
        # Access protected resource with invalid token
        response = self.client.get(
            '/protected',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Invalid token')
    
    def test_access_role_protected_resource(self):
        # Register admin user
        self.client.post(
            '/auth/register',
            data={'username': 'adminuser', 'password': 'AdminPass123!', 
                  'email': 'admin@example.com', 'roles': ['admin']}
        )
        
        # Register editor user
        self.client.post(
            '/auth/register',
            data={'username': 'editoruser', 'password': 'EditorPass123!', 
                  'email': 'editor@example.com', 'roles': ['editor']}
        )
        
        # Register viewer user
        self.client.post(
            '/auth/register',
            data={'username': 'vieweruser', 'password': 'ViewerPass123!', 
                  'email': 'viewer@example.com', 'roles': ['viewer']}
        )
        
        # Login admin
        response = self.client.post(
            '/auth/login',
            data={'username': 'adminuser', 'password': 'AdminPass123!'}
        )
        admin_data = json.loads(response.data)
        admin_token = admin_data['access_token']
        
        # Login editor
        response = self.client.post(
            '/auth/login',
            data={'username': 'editoruser', 'password': 'EditorPass123!'}
        )
        editor_data = json.loads(response.data)
        editor_token = editor_data['access_token']
        
        # Login viewer
        response = self.client.post(
            '/auth/login',
            data={'username': 'vieweruser', 'password': 'ViewerPass123!'}
        )
        viewer_data = json.loads(response.data)
        viewer_token = viewer_data['access_token']
        
        # Test admin can access all resources
        response = self.client.get('/admin', headers={'Authorization': f'Bearer {admin_token}'})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/editor', headers={'Authorization': f'Bearer {admin_token}'})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/viewer', headers={'Authorization': f'Bearer {admin_token}'})
        self.assertEqual(response.status_code, 200)
        
        # Test editor can access editor and viewer resources
        response = self.client.get('/admin', headers={'Authorization': f'Bearer {editor_token}'})
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get('/editor', headers={'Authorization': f'Bearer {editor_token}'})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/viewer', headers={'Authorization': f'Bearer {editor_token}'})
        self.assertEqual(response.status_code, 200)
        
        # Test viewer can only access viewer resource
        response = self.client.get('/admin', headers={'Authorization': f'Bearer {viewer_token}'})
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get('/editor', headers={'Authorization': f'Bearer {viewer_token}'})
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get('/viewer', headers={'Authorization': f'Bearer {viewer_token}'})
        self.assertEqual(response.status_code, 200)
    
    def test_token_refresh(self):
        # Register user
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Login to get tokens
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'TestPass123!'}
        )
        data = json.loads(response.data)
        refresh_token = data['refresh_token']
        
        # Refresh token
        response = self.client.post(
            '/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertEqual(data['token_type'], 'Bearer')
        self.assertEqual(data['expires_in'], 3600)
    
    def test_token_logout(self):
        # Register user
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'TestPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Login to get tokens
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'TestPass123!'}
        )
        data = json.loads(response.data)
        access_token = data['access_token']
        
        # Logout
        response = self.client.delete(
            '/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Successfully logged out')
        
        # Try to access protected resource with logged out token
        response = self.client.get(
            '/protected',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token has been revoked')
    
    def test_password_change(self):
        # Register user
        self.client.post(
            '/auth/register',
            data={'username': 'testuser', 'password': 'OldPass123!', 
                  'email': 'test@example.com'}
        )
        
        # Login to get token
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'OldPass123!'}
        )
        data = json.loads(response.data)
        access_token = data['access_token']
        
        # Change password
        response = self.client.post(
            '/auth/change-password',
            data={'old_password': 'OldPass123!', 'new_password': 'NewPass456!'},
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Password changed successfully')
        
        # Test login with new password
        response = self.client.post(
            '/auth/login',
            data={'username': 'testuser', 'password': 'NewPass456!'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_token_expiration(self):
        # Create a token that expires immediately
        expired_token = generate_token('testuser')
        
        # Wait for token to expire
        time.sleep(1)
        
        # Try to access protected resource with expired token
        response = self.client.get(
            '/protected',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token has expired')


if __name__ == '__main__':
    unittest.main()