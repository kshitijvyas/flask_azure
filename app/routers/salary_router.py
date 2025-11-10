from flask import Blueprint, request, jsonify
from app import models, serializers, database

salary_bp = Blueprint('salary', __name__)

# SALARIES
@salary_bp.route('/salaries', methods=['GET'])
def get_salaries():
    salaries = models.Salary.query.all()
    salary_schema = serializers.SalarySchema(many=True)
    return jsonify(salary_schema.dump(salaries))

@salary_bp.route('/salaries/<int:salary_id>', methods=['GET'])
def get_salary(salary_id):
    salary = models.Salary.query.get_or_404(salary_id)
    salary_schema = serializers.SalarySchema()
    return jsonify(salary_schema.dump(salary))

@salary_bp.route('/salaries', methods=['POST'])
def create_salary():
    data = request.get_json()
    salary_schema = serializers.SalarySchema()
    salary = salary_schema.load(data, session=database.db.session)
    database.db.session.add(salary)
    database.db.session.commit()
    return jsonify(salary_schema.dump(salary)), 201

@salary_bp.route('/salaries/<int:salary_id>', methods=['PUT'])
def update_salary(salary_id):
    salary = models.Salary.query.get_or_404(salary_id)
    data = request.get_json()
    salary_schema = serializers.SalarySchema()
    salary = salary_schema.load(data, instance=salary, session=database.db.session, partial=True)
    database.db.session.commit()
    return jsonify(salary_schema.dump(salary))

@salary_bp.route('/salaries/<int:salary_id>', methods=['DELETE'])
def delete_salary(salary_id):
    salary = models.Salary.query.get_or_404(salary_id)
    database.db.session.delete(salary)
    database.db.session.commit()
    return jsonify({'message': 'Salary deleted successfully'}), 200
