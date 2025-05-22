from flask import Blueprint, request, jsonify
from app import db
from app.models.core_models import CWPackage

cwp_bp = Blueprint('cwp_bp', __name__, url_prefix='/cw-packages')

@cwp_bp.route('/list', methods=['GET'])
def list_cwps():
    cwps = CWPackage.query.all()
    return jsonify(cwps=[{'code': c.code, 'name': c.name, 'unit': c.unit, 'project_id': c.project_id} for c in cwps]), 200

@cwp_bp.route('/create', methods=['POST'])
def create_cwp():
    data = request.get_json() or {}
    code = data.get('code')
    name = data.get('name')
    if not code or not name:
        return jsonify(error='Missing required fields'), 400
    cwp = CWPackage(code=code, name=name, unit=data.get('unit'), project_id=data.get('project_id'))
    db.session.add(cwp)
    db.session.commit()
    return jsonify(message='CWPackage created', cwp={'code': cwp.code}), 201

@cwp_bp.route('/update/<string:code>', methods=['PUT'])
def update_cwp(code):
    cwp = CWPackage.query.get(code)
    if not cwp:
        return jsonify(error='CWPackage not found'), 404
    data = request.get_json() or {}
    cwp.name = data.get('name', cwp.name)
    cwp.unit = data.get('unit', cwp.unit)
    cwp.project_id = data.get('project_id', cwp.project_id)
    db.session.commit()
    return jsonify(message='CWPackage updated', cwp={'code': cwp.code}), 200

@cwp_bp.route('/delete/<string:code>', methods=['DELETE'])
def delete_cwp(code):
    cwp = CWPackage.query.get(code)
    if not cwp:
        return jsonify(error='CWPackage not found'), 404
    db.session.delete(cwp)
    db.session.commit()
    return jsonify(message='CWPackage deleted'), 200
