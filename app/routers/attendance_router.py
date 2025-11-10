from flask import Blueprint, request, jsonify
from app import models, serializers, database

attendance_bp = Blueprint('attendance', __name__)

# ATTENDANCES
@attendance_bp.route('/attendances', methods=['GET'])
def get_attendances():
    attendances = models.Attendance.query.all()
    attendance_schema = serializers.AttendanceSchema(many=True)
    return jsonify(attendance_schema.dump(attendances))

@attendance_bp.route('/attendances/<int:attendance_id>', methods=['GET'])
def get_attendance(attendance_id):
    attendance = models.Attendance.query.get_or_404(attendance_id)
    attendance_schema = serializers.AttendanceSchema()
    return jsonify(attendance_schema.dump(attendance))

@attendance_bp.route('/attendances', methods=['POST'])
def create_attendance():
    data = request.get_json()
    attendance_schema = serializers.AttendanceSchema()
    attendance = attendance_schema.load(data, session=database.db.session)
    database.db.session.add(attendance)
    database.db.session.commit()
    return jsonify(attendance_schema.dump(attendance)), 201

@attendance_bp.route('/attendances/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    attendance = models.Attendance.query.get_or_404(attendance_id)
    data = request.get_json()
    attendance_schema = serializers.AttendanceSchema()
    attendance = attendance_schema.load(data, instance=attendance, session=database.db.session, partial=True)
    database.db.session.commit()
    return jsonify(attendance_schema.dump(attendance))

@attendance_bp.route('/attendances/<int:attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    attendance = models.Attendance.query.get_or_404(attendance_id)
    database.db.session.delete(attendance)
    database.db.session.commit()
    return jsonify({'message': 'Attendance deleted successfully'}), 200