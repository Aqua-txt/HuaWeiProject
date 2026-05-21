from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from models import db, Review, Order, User, beijing_now
from utils.auth import login_required

review_bp = Blueprint('review', __name__)


def update_user_credit(user_id):
    reviews = Review.query.filter_by(reviewee_id=user_id).all()
    if not reviews:
        user = User.query.get(user_id)
        if user:
            user.credit_score = 0
            user.credit_count = 0
        return

    total_score = 0
    for r in reviews:
        score = r.communication_score * 0.2 + r.description_score * 0.5 + r.speed_score * 0.3
        total_score += score

    avg_score = total_score / len(reviews)
    user = User.query.get(user_id)
    if user:
        user.credit_score = avg_score
        user.credit_count = len(reviews)


@review_bp.route('/api/reviews', methods=['POST'])
@login_required
def create_review():
    data = request.get_json() or {}
    order_id = data.get('order_id')
    communication_score = data.get('communication_score')
    description_score = data.get('description_score')
    speed_score = data.get('speed_score')
    comment = data.get('comment', '').strip()

    if not order_id:
        return jsonify({'code': 400, 'message': '缺少订单ID'}), 400

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.status != '已完成':
        return jsonify({'code': 400, 'message': '只能评价已完成的订单'}), 404
    if g.current_user.id not in [order.buyer_id, order.seller_id]:
        return jsonify({'code': 403, 'message': '无权评价'}), 403

    if order.buyer_id == g.current_user.id:
        reviewee_id = order.seller_id
    else:
        reviewee_id = order.buyer_id

    existing = Review.query.filter_by(order_id=order_id, reviewer_id=g.current_user.id).first()
    if existing:
        return jsonify({'code': 400, 'message': '已评价过该订单'}), 400

    deadline = order.updated_at + timedelta(days=7)
    if beijing_now() > deadline:
        return jsonify({'code': 400, 'message': '评价已过期（交易完成后7天内有效）'}), 400

    for score in [communication_score, description_score, speed_score]:
        if score is None or score < 1 or score > 5:
            return jsonify({'code': 400, 'message': '评分需在1-5之间'}), 400

    if len(comment) > 200:
        return jsonify({'code': 400, 'message': '评价文字不能超过200字'}), 400

    review = Review(
        order_id=order_id,
        reviewer_id=g.current_user.id,
        reviewee_id=reviewee_id,
        communication_score=communication_score,
        description_score=description_score,
        speed_score=speed_score,
        comment=comment,
    )
    db.session.add(review)
    db.session.commit()

    update_user_credit(reviewee_id)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '评价成功',
        'data': review.to_dict()
    })


@review_bp.route('/api/reviews', methods=['GET'])
@login_required
def list_reviews():
    user_id = request.args.get('user_id', type=int)
    reviewee_id = request.args.get('reviewee_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Review.query

    if user_id:
        query = query.filter(Review.reviewer_id == user_id)
    elif reviewee_id:
        query = query.filter(Review.reviewee_id == reviewee_id)
    else:
        return jsonify({'code': 400, 'message': '缺少user_id或reviewee_id参数'}), 400

    query = query.order_by(Review.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'reviews': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@review_bp.route('/api/reviews/<int:review_id>', methods=['GET'])
@login_required
def get_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'code': 404, 'message': '评价不存在'}), 404

    return jsonify({'code': 200, 'data': review.to_dict()})


@review_bp.route('/api/orders/<int:order_id>/reviewable', methods=['GET'])
@login_required
def check_reviewable(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404
    if order.status != '已完成':
        return jsonify({'code': 200, 'data': {'reviewable': False, 'reason': '订单未完成'}})
    if g.current_user.id not in [order.buyer_id, order.seller_id]:
        return jsonify({'code': 200, 'data': {'reviewable': False, 'reason': '无权评价'}})

    existing = Review.query.filter_by(order_id=order_id, reviewer_id=g.current_user.id).first()
    if existing:
        return jsonify({'code': 200, 'data': {'reviewable': False, 'reason': '已评价', 'review': existing.to_dict()}})

    if order.buyer_confirmed_at:
        deadline = order.buyer_confirmed_at + timedelta(days=7)
    else:
        deadline = order.updated_at + timedelta(days=7)

    if beijing_now() > deadline:
        return jsonify({'code': 200, 'data': {'reviewable': False, 'reason': '评价已过期'}})

    return jsonify({'code': 200, 'data': {'reviewable': True}})
