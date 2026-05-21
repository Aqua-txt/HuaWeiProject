import uuid
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Report, Product, User, Order, Review, Wanted, beijing_now
from utils.auth import create_token

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    import jwt
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
            if payload.get('role') != 'admin':
                return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
            admin = Admin.query.get(payload['admin_id'])
            if not admin:
                return jsonify({'code': 401, 'message': '管理员不存在'}), 401
            g.current_admin = admin
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效的登录凭证'}), 401

        return f(*args, **kwargs)
    return decorated


def create_admin_token(admin_id):
    import jwt
    now = datetime.now(timezone.utc)
    payload = {
        'admin_id': admin_id,
        'role': 'admin',
        'exp': now + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': now,
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


import jwt


@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'code': 400, 'message': '用户名或密码错误'}), 400

    token = create_admin_token(admin.id)
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {'token': token, 'admin': admin.to_dict()}
    })


@admin_bp.route('/api/admin/init', methods=['POST'])
def init_admin():
    existing = Admin.query.first()
    if existing:
        return jsonify({'code': 400, 'message': '管理员已存在'}), 400

    data = request.get_json() or {}
    username = data.get('username', 'admin').strip()
    password = data.get('password', 'admin123')

    admin = Admin(
        username=username,
        password_hash=generate_password_hash(password),
        role='admin',
    )
    db.session.add(admin)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '管理员初始化成功',
        'data': admin.to_dict()
    })


@admin_bp.route('/api/admin/reports', methods=['GET'])
@admin_required
def list_reports():
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Report.query
    if status:
        query = query.filter(Report.status == status)

    query = query.order_by(Report.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'reports': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@admin_bp.route('/api/admin/reports/<int:report_id>', methods=['GET'])
@admin_required
def get_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '举报不存在'}), 404

    data = report.to_dict()
    if report.product_id:
        product = Product.query.get(report.product_id)
        data['product'] = product.to_dict() if product else None

    return jsonify({'code': 200, 'data': data})


@admin_bp.route('/api/admin/reports/<int:report_id>/handle', methods=['POST'])
@admin_required
def handle_report(report_id):
    data = request.get_json() or {}
    action = data.get('action', '').strip()
    note = data.get('note', '').strip()

    if action not in ['reject', 'takedown', 'ban']:
        return jsonify({'code': 400, 'message': '无效的操作'}), 400

    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '举报不存在'}), 404
    if report.status != '待处理':
        return jsonify({'code': 400, 'message': '举报已处理'}), 400

    if action == 'reject':
        report.status = '已驳回'
        report.handler_note = note or '举报无效，已驳回'
    elif action == 'takedown':
        product = Product.query.get(report.product_id)
        if product:
            product.status = '已下架'
        report.status = '已处理'
        report.handler_note = note or '商品已下架'
    elif action == 'ban':
        product = Product.query.get(report.product_id)
        if product:
            product.status = '已下架'
            seller = User.query.get(product.seller_id)
            if seller:
                seller.is_banned = True
        report.status = '已处理'
        report.handler_note = note or '商品已下架，用户已封禁'

    report.handled_at = beijing_now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '处理成功',
        'data': report.to_dict()
    })


@admin_bp.route('/api/admin/products', methods=['GET'])
@admin_required
def list_products():
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Product.query

    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(Product.title.like(like), Product.description.like(like))
        )
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)

    query = query.order_by(Product.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'products': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@admin_bp.route('/api/admin/products/<int:product_id>/status', methods=['PUT'])
@admin_required
def update_product_status(product_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip()

    if new_status not in ['上架', '已下架']:
        return jsonify({'code': 400, 'message': '无效的状态'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404

    product.status = new_status
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '状态更新成功',
        'data': product.to_dict()
    })


@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def list_users():
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = User.query

    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(User.student_id.like(like), User.nickname.like(like))
        )

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@admin_bp.route('/api/admin/users/<int:user_id>/ban', methods=['PUT'])
@admin_required
def toggle_user_ban(user_id):
    data = request.get_json() or {}
    is_banned = data.get('is_banned')

    if is_banned is None:
        return jsonify({'code': 400, 'message': '缺少封禁状态'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    user.is_banned = is_banned
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '封禁状态更新成功',
        'data': user.to_dict()
    })


@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def dashboard():
    today = beijing_now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_orders = Order.query.filter(Order.created_at >= today).count()
    today_products = Product.query.filter(Product.created_at >= today).count()
    today_users = User.query.filter(User.created_at >= today).count()

    total_products = Product.query.count()
    total_users = User.query.filter(User.is_banned == False).count()
    total_orders = Order.query.count()
    paid_orders = Order.query.filter(Order.status.in_(['已付款', '已完成', '已退款'])).count()
    completed_orders = Order.query.filter(Order.status == '已完成').count()

    # trend: last 30 days
    daily_stats = []
    for i in range(30):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_orders = Order.query.filter(
            Order.created_at >= day_start,
            Order.created_at < day_end
        ).count()

        day_products = Product.query.filter(
            Product.created_at >= day_start,
            Product.created_at < day_end
        ).count()

        day_users = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()

        daily_stats.append({
            'date': day_start.strftime('%m-%d'),
            'orders': day_orders,
            'products': day_products,
            'users': day_users,
        })

    # category distribution
    category_stats = []
    categories = ['教材', '数码', '生活', '其他']
    for cat in categories:
        count = Product.query.filter(Product.category == cat).count()
        category_stats.append({'category': cat, 'count': count})

    return jsonify({
        'code': 200,
        'data': {
            'overview': {
                'today_orders': today_orders,
                'today_products': today_products,
                'today_users': today_users,
                'total_products': total_products,
                'total_users': total_users,
                'total_orders': total_orders,
                'paid_orders': paid_orders,
                'completed_orders': completed_orders,
            },
            'trend': list(reversed(daily_stats)),
            'category_distribution': category_stats,
        }
    })
