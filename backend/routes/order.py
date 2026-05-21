from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Order, Product
from utils.auth import login_required
import random
import string

order_bp = Blueprint('order', __name__, url_prefix='/api')


def generate_order_no():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f'ORD{timestamp}{random_str}'


@order_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'code': 400, 'message': '缺少商品ID'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    if product.seller_id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能购买自己的商品'}), 400
    
    if product.status != '上架':
        return jsonify({'code': 400, 'message': '商品已下架或已删除'}), 400
    
    order = Order(
        order_no=generate_order_no(),
        product_id=product_id,
        buyer_id=g.current_user.id,
        seller_id=product.seller_id,
        price=product.price,
        status='待支付'
    )
    
    product.status = '已下架'
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '订单创建成功',
        'data': order.to_dict()
    })


@order_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    role = request.args.get('role', 'buyer')
    status = request.args.get('status')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Order.query
    
    if role == 'buyer':
        query = query.filter_by(buyer_id=g.current_user.id)
    elif role == 'seller':
        query = query.filter_by(seller_id=g.current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    orders = [order.to_dict() for order in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'orders': orders,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id and order.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权查看此订单'}), 403
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': order.to_dict()
    })


@order_bp.route('/orders/<int:order_id>/ship', methods=['POST'])
@login_required
def ship_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有卖家能发货'}), 403
    
    if order.status != '待发货':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400
    
    order.status = '已发货'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发货成功',
        'data': order.to_dict()
    })


@order_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_receive(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有买家能确认收货'}), 403
    
    if order.status != '已发货':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400
    
    order.status = '已完成'
    order.completed_at = datetime.utcnow()
    
    product = Product.query.get(order.product_id)
    if product:
        product.status = '已删除'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '确认收货成功',
        'data': order.to_dict()
    })


@order_bp.route('/orders/<int:order_id>/refund', methods=['POST'])
@login_required
def request_refund(order_id):
    data = request.get_json()
    reason = data.get('reason', '')
    
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有买家能申请退款'}), 403
    
    if order.status not in ['已支付', '待发货']:
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400
    
    order.refund_reason = reason
    order.refund_status = '退款申请中'
    order.status = '退款申请中'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '退款申请已提交',
        'data': order.to_dict()
    })


@order_bp.route('/orders/<int:order_id>/handle-refund', methods=['POST'])
@login_required
def handle_refund(order_id):
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['agree', 'reject']:
        return jsonify({'code': 400, 'message': '操作类型错误'}), 400
    
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只有卖家能处理退款'}), 403
    
    if order.status != '退款申请中':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400
    
    if action == 'agree':
        order.status = '已退款'
        order.refund_status = '已退款'
        order.refunded_at = datetime.utcnow()
        
        product = Product.query.get(order.product_id)
        if product:
            product.status = '上架'
    else:
        order.status = '已支付'
        order.refund_status = '退款已拒绝'
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '处理成功',
        'data': order.to_dict()
    })


@order_bp.route('/pay/mock-wechat-pay', methods=['POST'])
@login_required
def mock_payment():
    data = request.get_json()
    order_id = data.get('order_id')
    payment_method = data.get('payment_method', '微信支付')
    
    if not order_id:
        return jsonify({'code': 400, 'message': '缺少订单ID'}), 400
    
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权支付此订单'}), 403
    
    if order.status != '待支付':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400
    
    transaction_id = f'MOCK{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(100000, 999999)}'
    
    order.status = '待发货'
    order.payment_method = payment_method
    order.transaction_id = transaction_id
    order.paid_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '支付成功',
        'data': {
            'order_id': order.id,
            'transaction_id': transaction_id,
            'status': order.status
        }
    })
