from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Order, Review, User
from utils.auth import login_required

review_bp = Blueprint('review', __name__, url_prefix='/api')


@review_bp.route('/reviews', methods=['POST'])
@login_required
def create_review():
    data = request.get_json()
    order_id = data.get('order_id')
    rating = data.get('rating')
    content = data.get('content', '')
    
    if not order_id or not rating:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    if rating < 1 or rating > 5:
        return jsonify({'code': 400, 'message': '评分必须在1-5之间'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只能评价自己的订单'}), 403
    
    if order.status != '已完成':
        return jsonify({'code': 400, 'message': '订单未完成，无法评价'}), 400
    
    existing_review = Review.query.filter_by(order_id=order_id).first()
    if existing_review:
        return jsonify({'code': 400, 'message': '该订单已评价'}), 400
    
    review = Review(
        order_id=order_id,
        reviewer_id=g.current_user.id,
        reviewee_id=order.seller_id,
        rating=rating,
        content=content
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '评价成功',
        'data': review.to_dict()
    })


@review_bp.route('/reviews/user/<int:user_id>', methods=['GET'])
def get_reviews_by_user(user_id):
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    
    pagination = Review.query.filter_by(reviewee_id=user_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    reviews = [review.to_dict() for review in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reviews': reviews,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@review_bp.route('/reviews/my', methods=['GET'])
@login_required
def get_my_reviews():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    pagination = Review.query.filter_by(reviewer_id=g.current_user.id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    reviews = [review.to_dict() for review in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reviews': reviews,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@review_bp.route('/reviews/check/<int:order_id>', methods=['GET'])
@login_required
def check_reviewed(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    
    if order.buyer_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权查看'}), 403
    
    review = Review.query.filter_by(order_id=order_id).first()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reviewed': review is not None,
            'review': review.to_dict() if review else None
        }
    })
