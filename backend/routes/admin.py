from datetime import datetime
from functools import wraps
import jwt
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, User, Product, Order, Report
from utils.auth import create_token

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
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
            admin = Admin.query.get(payload.get('user_id'))
            if not admin:
                return jsonify({'code': 401, 'message': '管理员不存在'}), 401
            g.current_admin = admin
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效凭证'}), 401
        
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    token = create_token(admin.id)
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'admin': admin.to_dict()
        }
    })


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    total_users = User.query.count()
    total_products = Product.query.count()
    active_products = Product.query.filter_by(status='上架').count()
    total_orders = Order.query.count()
    completed_orders = Order.query.filter_by(status='已完成').count()
    pending_reports = Report.query.filter_by(status='待处理').count()
    
    total_revenue = db.session.query(db.func.sum(Order.price)).filter(
        Order.status == '已完成'
    ).scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    category_stats = db.session.query(
        Product.category,
        db.func.count(Product.id)
    ).filter(Product.status == '上架').group_by(Product.category).all()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total_users': total_users,
            'total_products': total_products,
            'active_products': active_products,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_reports': pending_reports,
            'total_revenue': total_revenue,
            'recent_orders': [order.to_dict() for order in recent_orders],
            'category_stats': [{'category': cat, 'count': count} for cat, count in category_stats]
        }
    })


@admin_bp.route('/reports', methods=['GET'])
@admin_required
def get_reports():
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Report.query
    
    if status:
        status_map = {
            'pending': '待处理',
            'handled': '已处理',
            'rejected': '已驳回',
            '待处理': '待处理',
            '已处理': '已处理',
            '已驳回': '已驳回',
        }
        status = status_map.get(status, status)
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Report.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reports = []
    for report in pagination.items:
        report_dict = report.to_dict()
        report_dict['reporter'] = {
            'nickname': report.reporter.nickname if report.reporter else '未知'
        }
        report_dict['product'] = {
            'title': report.product.title if report.product else '已删除'
        }
        report_dict['report_type'] = report.reason
        report_dict['status'] = 'pending' if report.status == '待处理' else 'handled'
        reports.append(report_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reports': reports,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@admin_bp.route('/reports/<int:report_id>/handle', methods=['POST'])
@admin_required
def handle_report(report_id):
    data = request.get_json()
    action = data.get('action')
    result = data.get('result', '') or data.get('note', '')
    
    valid_actions = ['approve', 'reject', 'takedown', 'ban']
    if action not in valid_actions:
        return jsonify({'code': 400, 'message': '操作类型错误'}), 400
    
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '举报不存在'}), 404
    
    if report.status != '待处理':
        return jsonify({'code': 400, 'message': '该举报已处理'}), 400
    
    report.handler_id = g.current_admin.id
    report.handle_result = result
    report.handled_at = datetime.utcnow()
    
    if action in ['approve', 'takedown']:
        report.status = '已处理'
        product = Product.query.get(report.product_id)
        if product:
            product.status = '已删除'
    else:
        report.status = '已驳回'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '处理成功',
        'data': report.to_dict()
    })


@admin_bp.route('/products', methods=['GET'])
@admin_required
def get_products():
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Product.query
    
    if status:
        query = query.filter_by(status=status)
    
    if keyword:
        query = query.filter(Product.title.contains(keyword))
    
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    products = [product.to_dict() for product in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'products': products,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@admin_bp.route('/products/<int:product_id>/toggle', methods=['POST'])
@admin_required
def toggle_product(product_id):
    product = Product.query.get(product_id)
    
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    if product.status == '上架':
        product.status = '已下架'
    elif product.status == '已下架':
        product.status = '上架'
    else:
        return jsonify({'code': 400, 'message': '无法修改此商品状态'}), 400
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '操作成功',
        'data': product.to_dict()
    })


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    keyword = request.args.get('keyword')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = User.query
    
    if keyword:
        query = query.filter(
            db.or_(
                User.nickname.contains(keyword),
                User.student_id.contains(keyword)
            )
        )
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = []
    for user in pagination.items:
        user_dict = user.to_dict()
        user_dict['product_count'] = Product.query.filter_by(seller_id=user.id).count()
        user_dict['order_count'] = Order.query.filter_by(buyer_id=user.id).count()
        users.append(user_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'users': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    return jsonify({
        'code': 200,
        'message': '功能暂未实现'
    })
