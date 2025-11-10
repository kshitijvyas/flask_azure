import app.models as models
import app.serializers as serializers
import app.database as database

class UserService:

    def get_all_users(self):
        users = models.User.query.all()
        user_schema = serializers.UserSchema(many=True)
        return user_schema.dump(users)

    def get_user(self, user_id):
        user = models.User.query.get_or_404(user_id)
        user_schema = serializers.UserSchema()
        return user_schema.dump(user)

    def create_user(self, data):
        user_schema = serializers.UserSchema()
        user = user_schema.load(data, session=database.db.session)
        database.db.session.add(user)
        database.db.session.commit()
        return user_schema.dump(user)

    def update_user(self, user_id, data):
        user = models.User.query.get_or_404(user_id)
        user_schema = serializers.UserSchema()
        user = user_schema.load(data, instance=user, session=database.db.session, partial=True)
        database.db.session.commit()
        return user_schema.dump(user)

    def delete_user(self, user_id):
        user = models.User.query.get_or_404(user_id)
        database.db.session.delete(user)
        database.db.session.commit()
        return {'message': 'User deleted successfully'}