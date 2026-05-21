from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g
from models import db, Wanted, WantedResponse, Product
from utils.auth import login_required, optional_login

wanted_bp = Blueprint('wanted', __name__)


@wanted_bp.route('/api/wanteds', methods=['POST'])
@login_required
def create_wanted():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    budget_min = data.get('budget_min', 0)
    budget_max = data.get('budget_max', 99999.99)
    category = data.get('category', '其他').strip()
    desired_condition = data.get('desired_condition', '').strip()

    if not title:
        return jsonify({'code': 400, 'message': '请输入标题'}), 400
    if len(title) > 100:
        return jsonify({'code': 400, 'message': '标题不能超过100字'}), 400

    try:
        budget_min = float(budget_min)
        budget_max = float(budget_max)
        if budget_min < 0 or budget_max < 0 or budget_min > budget_max:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'code': 400, 'message': '预算范围无效'}), 400

    valid_categories = ['教材', '数码', '生活', '其他', '数码电子', '图书教材', '生活用品', '服装配饰', '运动户外', '美妆护肤', '食品零食']
    if category not in valid_categories:
        category = '其他'

    wanted = Wanted(
        user_id=g.current_user.id,
        title=title,
        description=description,
        budget_min=budget_min,
        budget_max=budget_max,
        category=category,
        desired_condition=desired_condition,
        status='进行中',
    )
    db.session.add(wanted)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '求购发布成功',
        'data': wanted.to_dict()
    })


@wanted_bp.route('/api/wanteds', methods=['GET'])
@optional_login
def list_wanteds():
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '')
    mine = request.args.get('mine', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Wanted.query

    if category:
        query = query.filter(Wanted.category == category)
    if status:
        query = query.filter(Wanted.status == status)
    if mine and g.current_user:
        query = query.filter(Wanted.user_id == g.current_user.id)

    query = query.order_by(Wanted.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'wanteds': [w.to_dict() for w in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@wanted_bp.route('/api/wanteds/<int:wanted_id>', methods=['GET'])
@optional_login
def get_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购不存在'}), 404

    data = wanted.to_dict()
    responses = WantedResponse.query.filter_by(wanted_id=wanted_id).order_by(
        WantedResponse.created_at.desc()
    ).all()
    data['responses'] = [r.to_dict() for r in responses]

    recommended_products = Product.query.filter(
        Product.status == '上架',
        Product.category == wanted.category,
        Product.price >= wanted.budget_min,
        Product.price <= wanted.budget_max,
    ).order_by(Product.created_at.desc()).limit(5).all()
    data['recommended_products'] = [p.to_dict() for p in recommended_products]

    return jsonify({'code': 200, 'data': data})


@wanted_bp.route('/api/wanteds/<int:wanted_id>', methods=['PUT'])
@login_required
def update_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购不存在'}), 404
    if wanted.user_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description')
    budget_min = data.get('budget_min')
    budget_max = data.get('budget_max')
    category = data.get('category')
    desired_condition = data.get('desired_condition')
    status = data.get('status', '').strip()

    if title:
        if len(title) > 100:
            return jsonify({'code': 400, 'message': '标题不能超过100字'}), 400
        wanted.title = title
    if description is not None:
        wanted.description = description.strip()
    if budget_min is not None:
        try:
            wanted.budget_min = float(budget_min)
        except (ValueError, TypeError):
            pass
    if budget_max is not None:
        try:
            wanted.budget_max = float(budget_max)
        except (ValueError, TypeError):
            pass
    if category and category in ['教材', '数码', '生活', '其他']:
        wanted.category = category
    if desired_condition is not None:
        wanted.desired_condition = desired_condition.strip()
    if status and status in ['进行中', '已关闭']:
        wanted.status = status

    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': wanted.to_dict()
    })


@wanted_bp.route('/api/wanteds/<int:wanted_id>', methods=['DELETE'])
@login_required
def delete_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购不存在'}), 404
    if wanted.user_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权操作'}), 403

    WantedResponse.query.filter_by(wanted_id=wanted_id).delete()
    db.session.delete(wanted)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@wanted_bp.route('/api/wanteds/<int:wanted_id>/responses', methods=['POST'])
@login_required
def create_wanted_response(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购不存在'}), 404
    if wanted.status != '进行中':
        return jsonify({'code': 400, 'message': '求购已关闭'}), 400
    if wanted.user_id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能响应自己的求购'}), 400

    data = request.get_json() or {}
    price_offer = data.get('price_offer')
    message = data.get('message', '').strip()
    product_id = data.get('product_id')

    if price_offer is None:
        return jsonify({'code': 400, 'message': '请填写报价'}), 400
    try:
        price_offer = float(price_offer)
        if price_offer < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'code': 400, 'message': '报价无效'}), 400

    if product_id:
        product = Product.query.get(product_id)
        if not product or product.seller_id != g.current_user.id:
            return jsonify({'code': 400, 'message': '无效的关联商品'}), 400

    response = WantedResponse(
        wanted_id=wanted_id,
        responder_id=g.current_user.id,
        price_offer=price_offer,
        message=message,
        product_id=product_id,
    )
    db.session.add(response)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '响应成功',
        'data': response.to_dict()
    })


@wanted_bp.route('/api/wanteds/<int:wanted_id>/responses', methods=['GET'])
@login_required
def list_wanted_responses(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购不存在'}), 404

    responses = WantedResponse.query.filter_by(wanted_id=wanted_id).order_by(
        WantedResponse.created_at.desc()
    ).all()

    return jsonify({
        'code': 200,
        'data': {
            'responses': [r.to_dict() for r in responses]
        }
    })
