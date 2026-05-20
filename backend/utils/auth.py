from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import request, jsonify, current_app, g
from models import User


def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if not token:
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'code': 401, 'message': '用户不存在'}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效的登录凭证'}), 401

        return f(*args, **kwargs)
    return decorated


def optional_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        g.current_user = None
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        if token:
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                user = User.query.get(payload['user_id'])
                g.current_user = user
            except Exception:
                pass
        return f(*args, **kwargs)
    return decorated
