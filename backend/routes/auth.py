from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils.auth import create_token, login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    student_id = data.get('student_id', '').strip()
    nickname = data.get('nickname', '').strip()
    password = data.get('password', '')

    if not student_id or not nickname or not password:
        return jsonify({'code': 400, 'message': '学号、昵称和密码不能为空'}), 400
    if len(student_id) < 4 or len(student_id) > 20:
        return jsonify({'code': 400, 'message': '学号长度需在4-20位之间'}), 400
    if len(nickname) > 50:
        return jsonify({'code': 400, 'message': '昵称长度不能超过50个字符'}), 400
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400

    existing = User.query.filter_by(student_id=student_id).first()
    if existing:
        return jsonify({'code': 400, 'message': '该学号已注册'}), 400

    user = User(
        student_id=student_id,
        nickname=nickname,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    token = create_token(user.id)
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {'token': token, 'user': user.to_dict()}
    })


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    student_id = data.get('student_id', '').strip()
    password = data.get('password', '')

    if not student_id or not password:
        return jsonify({'code': 400, 'message': '学号和密码不能为空'}), 400

    user = User.query.filter_by(student_id=student_id).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 400, 'message': '学号或密码错误'}), 400

    token = create_token(user.id)
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {'token': token, 'user': user.to_dict()}
    })


@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_me():
    return jsonify({
        'code': 200,
        'data': {'user': g.current_user.to_dict()}
    })
