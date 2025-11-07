import sys
import os
# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('..'))
# Import the fields module directly from the current directory
import flask_restful.fields as fields
from flask_restful import marshal

# Define the data models
class User(object):
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.posts = []

class Post(object):
    def __init__(self, id, title, content, author):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.comments = []

class Comment(object):
    def __init__(self, id, text, author, post):
        self.id = id
        self.text = text
        self.author = author
        self.post = post

# Create sample data
user1 = User(1, "John Doe", "john@example.com")
user2 = User(2, "Jane Smith", "jane@example.com")

post1 = Post(1, "First Post", "This is the first post", user1)
post2 = Post(2, "Second Post", "This is the second post", user1)

comment1 = Comment(1, "Great post!", user2, post1)
comment2 = Comment(2, "Thanks for sharing", user1, post1)
comment3 = Comment(3, "Interesting read", user2, post2)

# Establish relationships
user1.posts.extend([post1, post2])
post1.comments.extend([comment1, comment2])
post2.comments.append(comment3)

# Define serialization fields
comment_fields = {
    'id': fields.Integer,
    'text': fields.String,
    'author': fields.Relationship({
        'id': fields.Integer,
        'name': fields.String
    }, relationship_type="one-to-one")
}

post_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'author': fields.Relationship({
        'id': fields.Integer,
        'name': fields.String
    }, relationship_type="one-to-one"),
    'comments': fields.Relationship(comment_fields, relationship_type="one-to-many")
}

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String(lazy=True),  # Lazy field - won't be serialized by default
    'posts': fields.Relationship(post_fields, relationship_type="one-to-many")
}

# Example 1: Basic serialization with circular reference detection
print("Example 1: Basic serialization with circular reference detection")
result = marshal(user1, user_fields)
print(f"User: {result['name']}")
print(f"Posts: {len(result['posts'])}")
for post in result['posts']:
    print(f"  Post: {post['title']}")
    print(f"  Comments: {len(post['comments'])}")
    for comment in post['comments']:
        print(f"    Comment: {comment['text']} by {comment['author']['name']}")
print()

# Example 2: Using only parameter to include specific fields
print("Example 2: Using only parameter to include specific fields")
result = marshal(user1, user_fields, only=['id', 'name'])
print(f"User (only id and name): {result}")
print()

# Example 3: Using exclude parameter to exclude fields
print("Example 3: Using exclude parameter to exclude fields")
result = marshal(user1, user_fields, exclude=['email'])
print(f"User (exclude email): {result.keys()}")
print()

# Example 4: Using depth parameter to limit nesting
print("Example 4: Using depth parameter to limit nesting")
result = marshal(user1, user_fields, depth=2)
print(f"User: {result['name']}")
print(f"Posts: {len(result['posts'])}")
for post in result['posts']:
    print(f"  Post: {post['title']}")
    print(f"  Comments: {len(post['comments'])}")
    # Comments won't have author field due to depth limit
    for comment in post['comments']:
        print(f"    Comment: {comment['text']} (author: {'present' if 'author' in comment else 'not present'})")
print()

# Example 5: Using lazy parameter
print("Example 5: Using lazy parameter")
result = marshal(user1, user_fields)
print(f"User (default - lazy fields excluded): {result.keys()}")
# Note: Currently, there's no mechanism to explicitly request lazy fields
# This would require additional implementation in the marshal function
print()

# Example 6: Serializing a single post with relationships
print("Example 6: Serializing a single post with relationships")
result = marshal(post1, post_fields)
print(f"Post: {result['title']}")
print(f"Author: {result['author']['name']}")
print(f"Comments: {len(result['comments'])}")
for comment in result['comments']:
    print(f"  Comment: {comment['text']} by {comment['author']['name']}")
print()

print("All examples completed successfully!")