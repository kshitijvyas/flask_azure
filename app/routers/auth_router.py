"""
Authentication Router
Handles user registration, login, token refresh, and logout
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.models import User
from app.database import db
from app.serializers import UserSchema
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    
    Request body:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securepassword123"
    }
    
    Returns:
    {
        "message": "User registered successfully",
        "user": {...},
        "access_token": "...",
        "refresh_token": "..."
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields: username, email, password'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f"New user registered: {user.username}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Login user and return JWT tokens
    
    Request body:
    {
        "username": "john_doe",  # or "email": "john@example.com"
        "password": "securepassword123"
    }
    
    Returns:
    {
        "message": "Login successful",
        "user": {...},
        "access_token": "...",
        "refresh_token": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find user by username or email
        username_or_email = data.get('username') or data.get('email')
        if not username_or_email:
            return jsonify({'error': 'Username or email required'}), 400
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Returns:
    {
        "access_token": "..."
    }
    """
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        logger.info(f"Token refreshed for user: {current_user_id}")
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500


@auth_bp.route('/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's information
    
    Headers:
        Authorization: Bearer <access_token>
    
    Returns:
    {
        "user": {...}
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user_schema.dump(user)
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500


@auth_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change current user's password
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request body:
    {
        "old_password": "currentpassword",
        "new_password": "newpassword123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Missing required fields: old_password, new_password'}), 400
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify old password
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Set new password
        user.set_password(data['new_password'])
        db.session.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed', 'details': str(e)}), 500
