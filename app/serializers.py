from app.models import User, Department, Salary, Attendance
from flask_marshmallow import Marshmallow

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True

class SalarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Salary
        load_instance = True

class AttendanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Attendance
        load_instance = True
