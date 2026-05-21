import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from models import db, Order, Payment, Product, User, beijing_now
from utils.auth import login_required

orders_bp = Blueprint('orders', __name__)


def generate_order_no():
    timestamp = beijing_now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:8]
    return f'ORD{timestamp}{random_str}'


def generate_transaction_id():
    return f'TXN{uuid.uuid4().hex[:16]}'


@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json() or {}
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({'code': 400, 'message': '缺少商品ID'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    if product.status != '上架':
        return jsonify({'code': 400, 'message': '商品已下架或已删除'}), 400
    if product.seller_id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能购买自己的商品'}), 400

    existing_order = Order.query.filter(
        Order.product_id == product_id,
        Order.buyer_id == g.current_user.id,
        Order.status.in_(['待付款', '已付款'])
    ).first()
    if existing_order:
        return jsonify({'code': 400, 'message': '该商品已有未完成订单'}), 400

    order = Order(
        order_no=generate_order_no(),
        buyer_id=g.current_user.id,
        seller_id=product.seller_id,
        product_id=product_id,
        amount=product.price,
        status='待付款',
    )
    db.session.add(order)
    product.status = '已下架'
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '订单创建成功',
        'data': order.to_dict()
    })


@orders_bp.route('/api/orders/<int:order_id>/pay', methods=['POST'])
@login_required
def mock_pay_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    if order.status != '待付款':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400

    existing_payment = Payment.query.filter_by(order_id=order_id, status='成功').first()
    if existing_payment:
        return jsonify({'code': 400, 'message': '订单已支付'}), 400

    transaction_id = generate_transaction_id()
    payment = Payment(
        order_id=order_id,
        user_id=g.current_user.id,
        amount=order.amount,
        transaction_id=transaction_id,
        status='成功',
        pay_type='wechat',
    )
    db.session.add(payment)

    order.status = '已付款'
    order.updated_at = beijing_now()

    product = Product.query.get(order.product_id)
    if product and product.status == '上架':
        product.status = '已下架'

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '支付成功',
        'data': {
            'order': order.to_dict(),
            'payment': payment.to_dict()
        }
    })


@orders_bp.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    if order.status != '待付款':
        return jsonify({'code': 400, 'message': '当前状态不能取消订单'}), 400

    order.status = '已取消'
    order.updated_at = beijing_now()

    product = Product.query.get(order.product_id)
    if product and product.status == '已下架':
        product.status = '上架'

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '订单已取消，商品已重新上架',
        'data': order.to_dict()
    })


@orders_bp.route('/api/orders/<int:order_id>/confirm', methods=['POST'])
@login_required
def confirm_receipt(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    if order.status != '已付款':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400

    order.status = '已完成'
    order.buyer_confirmed_at = beijing_now()
    order.updated_at = beijing_now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '确认收货成功，货款已打给卖家',
        'data': order.to_dict()
    })


@orders_bp.route('/api/orders/<int:order_id>/refund', methods=['POST'])
@login_required
def apply_refund(order_id):
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()

    if not reason or len(reason) < 10:
        return jsonify({'code': 400, 'message': '退款原因至少10个字'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    if order.status not in ['已付款']:
        return jsonify({'code': 400, 'message': '当前状态不能申请退款'}), 400

    order.status = '退款中'
    order.refund_reason = reason
    order.refund_status = '待处理'
    order.updated_at = beijing_now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '退款申请已提交',
        'data': order.to_dict()
    })


@orders_bp.route('/api/orders/<int:order_id>/refund/respond', methods=['POST'])
@login_required
def respond_refund(order_id):
    data = request.get_json() or {}
    agree = data.get('agree')
    note = data.get('note', '').strip()

    if agree is None:
        return jsonify({'code': 400, 'message': '缺少同意/拒绝参数'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403
    if order.status != '退款中':
        return jsonify({'code': 400, 'message': '订单状态不正确'}), 400

    if agree:
        order.status = '已退款'
        order.refund_status = '已同意'
        payment = Payment.query.filter_by(order_id=order_id, status='成功').first()
        if payment:
            refund_payment = Payment(
                order_id=order_id,
                user_id=order.buyer_id,
                amount=order.amount,
                transaction_id=generate_transaction_id(),
                status='已退款',
                pay_type='wechat_refund',
            )
            db.session.add(refund_payment)
        product = Product.query.get(order.product_id)
        if product and product.status == '已下架':
            product.status = '上架'
        msg = '退款已同意，款项已退回买家'
    else:
        order.status = '管理员仲裁'
        order.refund_status = '已拒绝'
        msg = '退款已拒绝，等待管理员介入'

    order.handler_note = note
    order.updated_at = beijing_now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': msg,
        'data': order.to_dict()
    })


@orders_bp.route('/api/orders', methods=['GET'])
@login_required
def list_orders():
    role = request.args.get('role', 'buyer')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Order.query
    if role == 'buyer':
        query = query.filter(Order.buyer_id == g.current_user.id)
    elif role == 'seller':
        query = query.filter(Order.seller_id == g.current_user.id)
    else:
        query = query.filter(
            db.or_(Order.buyer_id == g.current_user.id, Order.seller_id == g.current_user.id)
        )

    if status:
        query = query.filter(Order.status == status)

    query = query.order_by(Order.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'orders': [o.to_dict() for o in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@orders_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if g.current_user.id not in [order.buyer_id, order.seller_id]:
        return jsonify({'code': 403, 'message': '无权查看'}), 403

    data = order.to_dict()
    payments = Payment.query.filter_by(order_id=order_id).all()
    data['payments'] = [p.to_dict() for p in payments]

    return jsonify({'code': 200, 'data': data})
