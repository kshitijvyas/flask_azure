from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService
from app.services.storage_service import storage_service

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Public endpoint - list all users"""
    users = user_service.get_all_users()
    return jsonify(users)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Public endpoint - get user by ID"""
    user = user_service.get_user(user_id)
    return jsonify(user)

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Public endpoint - create user (deprecated - use /api/auth/register instead)
    This endpoint is kept for backward compatibility
    """
    data = request.get_json()
    user = user_service.create_user(data)
    return jsonify(user), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Protected endpoint - update user (must be authenticated)"""
    current_user_id = get_jwt_identity()
    
    # Users can only update their own profile (unless admin - RBAC coming next)
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized: You can only update your own profile'}), 403
    
    data = request.get_json()
    user = user_service.update_user(user_id, data)
    return jsonify(user)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Protected endpoint - delete user (must be authenticated)"""
    current_user_id = get_jwt_identity()
    
    # Users can only delete their own account (unless admin - RBAC coming next)
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized: You can only delete your own account'}), 403
    
    result = user_service.delete_user(user_id)
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar(user_id):
    """Protected endpoint - upload avatar (must be authenticated)"""
    current_user_id = get_jwt_identity()
    
    # Users can only upload their own avatar (unless admin - RBAC coming next)
    if current_user_id != user_id:
        return jsonify({'error': 'Unauthorized: You can only upload your own avatar'}), 403
    
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type (only images)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
    
    try:
        # Delete old avatar if exists
        if user.get('avatar_url'):
            storage_service.delete_file(user['avatar_url'])
        
        # Upload new avatar
        avatar_url = storage_service.upload_file(
            file_data=file.read(),
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Update user with new avatar URL
        updated_user = user_service.update_user(user_id, {'avatar_url': avatar_url})
        
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'avatar_url': avatar_url,
            'user': updated_user
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
