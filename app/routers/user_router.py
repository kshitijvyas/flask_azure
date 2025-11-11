from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.services.storage_service import storage_service

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = user_service.get_all_users()
    return jsonify(users)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_service.get_user(user_id)
    return jsonify(user)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = user_service.create_user(data)
    return jsonify(user), 201

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = user_service.update_user(user_id, data)
    return jsonify(user)

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = user_service.delete_user(user_id)
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>/upload-avatar', methods=['POST'])
def upload_avatar(user_id):
    """Upload avatar/profile picture for a user"""
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
