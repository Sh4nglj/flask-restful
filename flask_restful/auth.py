from __future__ import absolute_import
import jwt
import time
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app, g
import re

# Avoid circular import by importing flask_restful components inside functions/methods where needed


__all__ = ("Auth", "TokenBlacklist", "require_auth", "require_role",
           "auth_parser", "register_parser", "password_change_parser")

# In-memory storage (should be replaced with a database in production)
users = {}
token_blacklist = set()
login_attempts = {}

# Configuration defaults (will be overridden by Flask app config)
def get_config():
    """Get configuration from Flask app config with defaults"""
    return {
        # Token expiration times (in seconds)
        "ACCESS_TOKEN_EXPIRES": current_app.config.get("ACCESS_TOKEN_EXPIRES", 3600),  # 1 hour
        "REFRESH_TOKEN_EXPIRES": current_app.config.get("REFRESH_TOKEN_EXPIRES", 86400 * 7),  # 7 days
        # Password strength requirements
        "PASSWORD_MIN_LENGTH": current_app.config.get("PASSWORD_MIN_LENGTH", 8),
        "PASSWORD_REQUIRE_UPPERCASE": current_app.config.get("PASSWORD_REQUIRE_UPPERCASE", True),
        "PASSWORD_REQUIRE_LOWERCASE": current_app.config.get("PASSWORD_REQUIRE_LOWERCASE", True),
        "PASSWORD_REQUIRE_DIGITS": current_app.config.get("PASSWORD_REQUIRE_DIGITS", True),
        "PASSWORD_REQUIRE_SPECIAL": current_app.config.get("PASSWORD_REQUIRE_SPECIAL", True),
        # Login failure settings
        "MAX_LOGIN_ATTEMPTS": current_app.config.get("MAX_LOGIN_ATTEMPTS", 5),
        "ACCOUNT_LOCK_MINUTES": current_app.config.get("ACCOUNT_LOCK_MINUTES", 15),
        # JWT configuration
        "JWT_SECRET_KEY": current_app.config.get("JWT_SECRET_KEY", "super-secret-key"),
        "JWT_ALGORITHM": current_app.config.get("JWT_ALGORITHM", "HS256")
    }

def generate_token(identity, token_type="access"):
    """Generate a JWT token"""
    # Read configuration from Flask app config
    jwt_secret_key = current_app.config.get("JWT_SECRET_KEY", "super-secret-key")
    jwt_algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    access_token_expires = current_app.config.get("ACCESS_TOKEN_EXPIRES", 3600)
    refresh_token_expires = current_app.config.get("REFRESH_TOKEN_EXPIRES", 86400 * 7)
    
    if token_type == "access":
        expires = datetime.utcnow() + timedelta(seconds=access_token_expires)
    elif token_type == "refresh":
        expires = datetime.utcnow() + timedelta(seconds=refresh_token_expires)
    else:
        raise ValueError("Invalid token type")
    
    payload = {
        "sub": identity,
        "exp": expires,
        "iat": datetime.utcnow(),
        "type": token_type
    }
    
    return jwt.encode(payload, jwt_secret_key, algorithm=jwt_algorithm)


def validate_token(token):
    """Validate a JWT token"""
    try:
        # Read configuration from Flask app config
        jwt_secret_key = current_app.config.get("JWT_SECRET_KEY", "super-secret-key")
        jwt_algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
        
        payload = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        
        # Check if token is blacklisted
        if token in token_blacklist:
            return False, "Token has been revoked"
        
        # Check token type
        if payload.get("type") != "access":
            return False, "Invalid token type"
        
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"


def refresh_token(refresh_token):
    """Refresh an access token using a refresh token"""
    try:
        # Read configuration from Flask app config
        jwt_secret_key = current_app.config.get("JWT_SECRET_KEY", "super-secret-key")
        jwt_algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
        
        payload = jwt.decode(refresh_token, jwt_secret_key, algorithms=[jwt_algorithm])
        
        # Check if token is blacklisted
        if refresh_token in token_blacklist:
            return False, "Refresh token has been revoked", None
        
        # Check token type
        if payload.get("type") != "refresh":
            return False, "Invalid token type", None
        
        # Generate new access token
        new_access_token = generate_token(payload["sub"], "access")
        return True, "Token refreshed successfully", new_access_token
    except jwt.ExpiredSignatureError:
        return False, "Refresh token has expired", None
    except jwt.InvalidTokenError:
        return False, "Invalid refresh token", None


def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def verify_password(hashed_password, password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def validate_password_strength(password):
    """Validate password strength"""
    config = get_config()
    
    # Check minimum length
    if len(password) < config["PASSWORD_MIN_LENGTH"]:
        return False, f"Password must be at least {config["PASSWORD_MIN_LENGTH"]} characters long"
    
    # Check for uppercase letters
    if config["PASSWORD_REQUIRE_UPPERCASE"] and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letters
    if config["PASSWORD_REQUIRE_LOWERCASE"] and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digits
    if config["PASSWORD_REQUIRE_DIGITS"] and not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit"
    
    # Check for special characters
    if config["PASSWORD_REQUIRE_SPECIAL"] and not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password strength is sufficient"


def check_login_attempts(username):
    """Check login attempts and lock account if needed"""
    attempts = login_attempts.get(username, {"count": 0, "locked_until": None})
    
    # Check if account is locked
    if attempts["locked_until"] and datetime.utcnow() < attempts["locked_until"]:
        remaining_time = (attempts["locked_until"] - datetime.utcnow()).seconds // 60
        return False, f"Account is locked. Please try again in {remaining_time} minutes."
    
    return True, "Account is not locked"


def increment_login_attempts(username):
    """Increment login attempts and lock account if threshold is reached"""
    config = get_config()
    attempts = login_attempts.get(username, {"count": 0, "locked_until": None})
    attempts["count"] += 1
    
    if attempts["count"] >= config["MAX_LOGIN_ATTEMPTS"]:
        attempts["locked_until"] = datetime.utcnow() + timedelta(minutes=config["ACCOUNT_LOCK_MINUTES"])
        
    login_attempts[username] = attempts


def reset_login_attempts(username):
    """Reset login attempts for a user"""
    if username in login_attempts:
        del login_attempts[username]


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask_restful import abort
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            abort(401, message="Authorization header is missing")
        
        try:
            token_type, token = auth_header.split()
            if token_type.lower() != "bearer":
                abort(401, message="Invalid token type. Use Bearer.")
        except ValueError:
            abort(401, message="Invalid Authorization header format")
        
        valid, payload = validate_token(token)
        if not valid:
            abort(401, message=payload)
        
        # Get user from in-memory storage
        user = users.get(payload["sub"])
        if not user:
            abort(401, message="User not found")
        
        # Add user to Flask g object
        g.user = user
        
        return f(*args, **kwargs)
    return decorated


def require_role(role):
    """Decorator to require a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from flask_restful import abort
            if not hasattr(g, "user"):
                abort(401, message="Authentication required")
            
            user_roles = g.user.get("roles", [])
            if role not in user_roles:
                abort(403, message=f"Insufficient permissions. Required role: {role}")
            
            return f(*args, **kwargs)
        return decorated
    return decorator





from flask_restful import Resource

class Auth(Resource):
    """Authentication resource for handling login, registration, and password changes"""
    
    def post(self, endpoint):
        from flask_restful import abort, reqparse
        # Create request parsers inside the method to avoid circular import
        # Create register parser with roles handling
        register_parser = reqparse.RequestParser()
        register_parser.add_argument("username", type=str, required=True, help="Username is required", location=['json', 'form'])
        register_parser.add_argument("password", type=str, required=True, help="Password is required", location=['json', 'form'])
        register_parser.add_argument("email", type=str, required=True, help="Email is required", location=['json', 'form'])
        
        # Handle roles parameter: accept both list and comma-separated string
        def parse_roles(value):
            """Parse roles parameter: accept both list and comma-separated string"""
            if isinstance(value, str):
                return [role.strip() for role in value.split(',') if role.strip()]
            elif isinstance(value, list):
                return value
            return []
        
        # Add roles parameter
        register_parser.add_argument("roles", type=parse_roles, default=["viewer"], help="User roles (admin, editor, viewer)", location=['json', 'form'])
        
        auth_parser = reqparse.RequestParser()
        auth_parser.add_argument("username", type=str, required=True, help="Username is required", location=['json', 'form'])
        auth_parser.add_argument("password", type=str, required=True, help="Password is required", location=['json', 'form'])
        
        password_change_parser = reqparse.RequestParser()
        password_change_parser.add_argument("old_password", type=str, required=True, help="Old password is required", location=['json', 'form'])
        password_change_parser.add_argument("new_password", type=str, required=True, help="New password is required", location=['json', 'form'])
        
        if endpoint == "register":
            args = register_parser.parse_args()
            
            # Check if username already exists
            if args["username"] in users:
                abort(400, message="Username already exists")
            
            # Validate password strength
            valid, message = validate_password_strength(args["password"])
            if not valid:
                abort(400, message=message)
            
            # Hash password
            hashed_password = hash_password(args["password"])
            
            # Create user
            users[args["username"]] = {
                "username": args["username"],
                "email": args["email"],
                "password": hashed_password,
                "roles": args["roles"]
            }
            
            return {"message": "User registered successfully"}, 201
            
        elif endpoint == "login":
            args = auth_parser.parse_args()
            
            # Check if account is locked
            valid, message = check_login_attempts(args["username"])
            if not valid:
                abort(401, message=message)
            
            # Check if user exists
            user = users.get(args["username"])
            if not user:
                increment_login_attempts(args["username"])
                abort(401, message="Invalid username or password")
            
            # Verify password
            if not verify_password(user["password"], args["password"]):
                increment_login_attempts(args["username"])
                abort(401, message="Invalid username or password")
            
            # Reset login attempts
            reset_login_attempts(args["username"])
            
            # Generate tokens
            access_token = generate_token(args["username"], "access")
            refresh_token = generate_token(args["username"], "refresh")
            
            config = get_config()
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": config["ACCESS_TOKEN_EXPIRES"]
            }, 200
            
        elif endpoint == "refresh":
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                abort(401, message="Authorization header is missing")
            
            try:
                token_type, refresh_token = auth_header.split()
                if token_type.lower() != "bearer":
                    abort(401, message="Invalid token type. Use Bearer.")
            except ValueError:
                abort(401, message="Invalid Authorization header format")
            
            valid, message, new_access_token = refresh_token(refresh_token)
            if not valid:
                abort(401, message=message)
            
            config = get_config()
            return {
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": config["ACCESS_TOKEN_EXPIRES"]
            }, 200
            
        elif endpoint == "change-password":
            @require_auth
            def change_password():
                args = password_change_parser.parse_args()
                
                # Verify old password
                if not verify_password(g.user["password"], args["old_password"]):
                    abort(401, message="Invalid old password")
                
                # Validate new password strength
                valid, message = validate_password_strength(args["new_password"])
                if not valid:
                    abort(400, message=message)
                
                # Hash new password
                hashed_password = hash_password(args["new_password"])
                
                # Update user password
                users[g.user["username"]]["password"] = hashed_password
                
                return {"message": "Password changed successfully"}, 200
            
            return change_password()
            
        else:
            abort(404, message="Endpoint not found")
    
    @require_auth
    def delete(self, endpoint):
        from flask_restful import abort
        if endpoint == "logout":
            # Get token from request
            auth_header = request.headers.get("Authorization")
            try:
                token_type, token = auth_header.split()
            except ValueError:
                abort(400, message="Invalid Authorization header format")
            
            # Add token to blacklist
            token_blacklist.add(token)
            
            return {"message": "Successfully logged out"}, 200
        else:
            abort(404, message="Endpoint not found")


class TokenBlacklist:
    """Class to manage token blacklist"""
    
    @staticmethod
    def add(token):
        token_blacklist.add(token)
    
    @staticmethod
    def remove(token):
        token_blacklist.discard(token)
    
    @staticmethod
    def contains(token):
        return token in token_blacklist
    
    @staticmethod
    def clear():
        token_blacklist.clear()