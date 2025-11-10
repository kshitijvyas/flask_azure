from flask import Blueprint, request, jsonify
from app import models, serializers, database

department_bp = Blueprint('department', __name__)

# DEPARTMENTS
@department_bp.route('/departments', methods=['GET'])
def get_departments():
    departments = models.Department.query.all()
    department_schema = serializers.DepartmentSchema(many=True)
    return jsonify(department_schema.dump(departments))

@department_bp.route('/departments/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    department = models.Department.query.get_or_404(dept_id)
    department_schema = serializers.DepartmentSchema()
    return jsonify(department_schema.dump(department))

@department_bp.route('/departments', methods=['POST'])
def create_department():
    data = request.get_json()
    department_schema = serializers.DepartmentSchema()
    department = department_schema.load(data, session=database.db.session)
    database.db.session.add(department)
    database.db.session.commit()
    return jsonify(department_schema.dump(department)), 201

@department_bp.route('/departments/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    department = models.Department.query.get_or_404(dept_id)
    data = request.get_json()
    department_schema = serializers.DepartmentSchema()
    department = department_schema.load(data, instance=department, session=database.db.session, partial=True)
    database.db.session.commit()
    return jsonify(department_schema.dump(department))

@department_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    department = models.Department.query.get_or_404(dept_id)
    database.db.session.delete(department)
    database.db.session.commit()
    return jsonify({'message': 'Department deleted successfully'}), 200
