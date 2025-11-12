import logging
import app.models as models
import app.serializers as serializers
import app.database as database
from app.services.cache_service import cache_service
from app.services.queue_service import queue_service

logger = logging.getLogger(__name__)

class UserService:

    def get_all_users(self):
        # Try cache first
        cache_key = 'users:all'
        cached_users = cache_service.get(cache_key)
        
        if cached_users is not None:
            logger.info(f"Cache HIT: {cache_key}")
            return cached_users
        
        # Cache miss - fetch from database
        logger.info(f"Cache MISS: {cache_key}")
        users = models.User.query.all()
        user_schema = serializers.UserSchema(many=True)
        result = user_schema.dump(users)
        
        # Cache for 5 minutes
        cache_service.set(cache_key, result, ttl=300)
        
        return result

    def get_user(self, user_id):
        # Try cache first
        cache_key = f'user:{user_id}'
        cached_user = cache_service.get(cache_key)
        
        if cached_user is not None:
            logger.info(f"Cache HIT: {cache_key}")
            return cached_user
        
        # Cache miss - fetch from database
        logger.info(f"Cache MISS: {cache_key}")
        user = models.User.query.get_or_404(user_id)
        user_schema = serializers.UserSchema()
        result = user_schema.dump(user)
        
        # Cache for 10 minutes (individual users accessed more frequently)
        cache_service.set(cache_key, result, ttl=600)
        
        return result

    def create_user(self, data):
        user_schema = serializers.UserSchema()
        user = user_schema.load(data, session=database.db.session)
        database.db.session.add(user)
        database.db.session.commit()
        
        # Get serialized user data
        result = user_schema.dump(user)
        
        # Invalidate all users cache when new user is created
        cache_service.delete('users:all')
        
        # Send notification to queue for async processing
        queue_service.send_user_created_notification(result)
        logger.info(f"User created and notification queued: {result['username']}")
        
        return result

    def update_user(self, user_id, data):
        user = models.User.query.get_or_404(user_id)
        user_schema = serializers.UserSchema()
        user = user_schema.load(data, instance=user, session=database.db.session, partial=True)
        database.db.session.commit()
        
        # Invalidate caches for this user and all users list
        cache_service.delete(f'user:{user_id}')
        cache_service.delete('users:all')
        
        return user_schema.dump(user)

    def delete_user(self, user_id):
        user = models.User.query.get_or_404(user_id)
        database.db.session.delete(user)
        database.db.session.commit()
        
        # Invalidate caches for this user and all users list
        cache_service.delete(f'user:{user_id}')
        cache_service.delete('users:all')
        
        return {'message': 'User deleted successfully'}