import app.models as models
import app.serializers as serializers
import app.database as database
from app.services.cache_service import cache_service

class UserService:

    def get_all_users(self):
        # Try cache first
        cache_key = 'users:all'
        cached_users = cache_service.get(cache_key)
        
        if cached_users is not None:
            print(f"Cache HIT: {cache_key}")
            return cached_users
        
        # Cache miss - fetch from database
        print(f"Cache MISS: {cache_key}")
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
            print(f"Cache HIT: {cache_key}")
            return cached_user
        
        # Cache miss - fetch from database
        print(f"Cache MISS: {cache_key}")
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
        
        # Invalidate all users cache when new user is created
        cache_service.delete('users:all')
        
        return user_schema.dump(user)

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