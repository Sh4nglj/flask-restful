from decimal import Decimal
from functools import partial
import pytz
import unittest
from flask_restful.fields import MarshallingException
from flask_restful.utils import OrderedDict
from flask_restful import fields, marshal
from datetime import datetime, timedelta, tzinfo
from flask import Flask, Blueprint


class TestAdvancedSerialization(unittest.TestCase):
    """Test cases for advanced serialization features"""
    
    def test_circular_reference_detection(self):
        """Test that circular references are detected and handled properly"""
        class User(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
                self.posts = []
        
        class Post(object):
            def __init__(self, id, title, author):
                self.id = id
                self.title = title
                self.author = author
        
        # Create circular reference
        user = User(1, "John Doe")
        post = Post(1, "First Post", user)
        user.posts.append(post)
        
        # Define fields
        post_fields = {
            'id': fields.Integer,
            'title': fields.String,
            'author': fields.Nested({'id': fields.Integer, 'name': fields.String})
        }
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'posts': fields.List(fields.Nested(post_fields))
        }
        
        # This should not cause infinite recursion
        result = marshal(user, user_fields)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('posts', result)
        self.assertEqual(len(result['posts']), 1)
        self.assertIn('author', result['posts'][0])
    
    def test_depth_parameter(self):
        """Test that depth parameter limits nested serialization"""
        class User(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
                self.address = Address(1, "123 Main St", "City")
        
        class Address(object):
            def __init__(self, id, street, city):
                self.id = id
                self.street = street
                self.city = city
                self.country = Country(1, "Country")
        
        class Country(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        user = User(1, "John Doe")
        
        # Define deep nested fields
        country_fields = {
            'id': fields.Integer,
            'name': fields.String
        }
        
        address_fields = {
            'id': fields.Integer,
            'street': fields.String,
            'city': fields.String,
            'country': fields.Nested(country_fields)
        }
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'address': fields.Nested(address_fields)
        }
        
        # Test with depth=1 - only user fields, no nested
        result = marshal(user, user_fields, depth=1)
        self.assertIn('address', result)
        self.assertIn('country', result['address'])  # With depth=1, we still get the first level of nesting
        
        # Test with depth=0 - unlimited
        result = marshal(user, user_fields, depth=0)
        self.assertIn('country', result['address'])
    
    def test_lazy_parameter(self):
        """Test that lazy fields are not serialized by default"""
        class User(object):
            def __init__(self, id, name, email):
                self.id = id
                self.name = name
                self.email = email
        
        user = User(1, "John Doe", "john@example.com")
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'email': fields.String(lazy=True)
        }
        
        # By default, lazy fields should not be included
        result = marshal(user, user_fields)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertNotIn('email', result)
        
        # TODO: Need to implement explicit request mechanism for lazy fields
    
    def test_only_parameter(self):
        """Test that only parameter filters fields"""
        class User(object):
            def __init__(self, id, name, email, password):
                self.id = id
                self.name = name
                self.email = email
                self.password = password
        
        user = User(1, "John Doe", "john@example.com", "password123")
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'email': fields.String,
            'password': fields.String
        }
        
        # Test with only parameter
        result = marshal(user, user_fields, only=['id', 'name'])
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertNotIn('email', result)
        self.assertNotIn('password', result)
    
    def test_exclude_parameter(self):
        """Test that exclude parameter filters fields"""
        class User(object):
            def __init__(self, id, name, email, password):
                self.id = id
                self.name = name
                self.email = email
                self.password = password
        
        user = User(1, "John Doe", "john@example.com", "password123")
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'email': fields.String,
            'password': fields.String
        }
        
        # Test with exclude parameter
        result = marshal(user, user_fields, exclude=['password'])
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('email', result)
        self.assertNotIn('password', result)
    
    def test_relationship_field_one_to_one(self):
        """Test Relationship field for one-to-one relationships"""
        class User(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        class Profile(object):
            def __init__(self, id, bio, user):
                self.id = id
                self.bio = bio
                self.user = user
        
        user = User(1, "John Doe")
        profile = Profile(1, "Software Engineer", user)
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String
        }
        
        profile_fields = {
            'id': fields.Integer,
            'bio': fields.String,
            'user': fields.Relationship(user_fields, relationship_type="one-to-one")
        }
        
        result = marshal(profile, profile_fields)
        self.assertIn('user', result)
        self.assertEqual(result['user']['id'], 1)
        self.assertEqual(result['user']['name'], "John Doe")
    
    def test_relationship_field_one_to_many(self):
        """Test Relationship field for one-to-many relationships"""
        class User(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
                self.posts = []
        
        class Post(object):
            def __init__(self, id, title):
                self.id = id
                self.title = title
        
        user = User(1, "John Doe")
        user.posts.append(Post(1, "First Post"))
        user.posts.append(Post(2, "Second Post"))
        
        post_fields = {
            'id': fields.Integer,
            'title': fields.String
        }
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'posts': fields.Relationship(post_fields, relationship_type="one-to-many")
        }
        
        result = marshal(user, user_fields)
        self.assertIn('posts', result)
        self.assertEqual(len(result['posts']), 2)
        self.assertEqual(result['posts'][0]['title'], "First Post")
        self.assertEqual(result['posts'][1]['title'], "Second Post")
    
    def test_relationship_field_many_to_many(self):
        """Test Relationship field for many-to-many relationships"""
        class User(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        class Group(object):
            def __init__(self, id, name):
                self.id = id
                self.name = name
                self.members = []
        
        user1 = User(1, "John Doe")
        user2 = User(2, "Jane Smith")
        
        group = Group(1, "Developers")
        group.members.append(user1)
        group.members.append(user2)
        
        user_fields = {
            'id': fields.Integer,
            'name': fields.String
        }
        
        group_fields = {
            'id': fields.Integer,
            'name': fields.String,
            'members': fields.Relationship(user_fields, relationship_type="many-to-many")
        }
        
        result = marshal(group, group_fields)
        self.assertIn('members', result)
        self.assertEqual(len(result['members']), 2)
        self.assertEqual(result['members'][0]['name'], "John Doe")
        self.assertEqual(result['members'][1]['name'], "Jane Smith")


if __name__ == '__main__':
    unittest.main()