from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Wanted, WantedResponse, Product
from utils.auth import login_required

wanted_bp = Blueprint('wanted', __name__, url_prefix='/api')


@wanted_bp.route('/wanteds', methods=['GET'])
def get_wanteds():
    category = request.args.get('category')
    keyword = request.args.get('keyword')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Wanted.query.filter_by(status='求购中')
    
    if category:
        query = query.filter_by(category=category)
    
    if keyword:
        query = query.filter(
            db.or_(
                Wanted.title.contains(keyword),
                Wanted.description.contains(keyword)
            )
        )
    
    pagination = query.order_by(Wanted.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    wanteds = [wanted.to_dict() for wanted in pagination.items]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'wanteds': wanteds,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })


@wanted_bp.route('/wanteds/<int:wanted_id>', methods=['GET'])
def get_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    
    if not wanted:
        return jsonify({'code': 404, 'message': '求购信息不存在'}), 404
    
    wanted_dict = wanted.to_dict()
    wanted_dict['user'] = {
        'id': wanted.user.id if wanted.user else None,
        'nickname': wanted.user.nickname if wanted.user else '',
        'avatar': wanted.user.avatar if wanted.user else ''
    }
    
    responses = WantedResponse.query.filter_by(wanted_id=wanted_id).order_by(
        WantedResponse.created_at.desc()
    ).all()
    responses_list = []
    for r in responses:
        r_dict = r.to_dict()
        r_dict['responder'] = {
            'id': r.responder.id if r.responder else None,
            'nickname': r.responder.nickname if r.responder else '',
            'avatar': r.responder.avatar if r.responder else ''
        }
        if r.product:
            r_dict['product'] = {
                'id': r.product.id,
                'title': r.product.title
            }
        responses_list.append(r_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'wanted': wanted_dict,
            'responses': responses_list,
            'related_products': []
        }
    })


@wanted_bp.route('/wanteds', methods=['POST'])
@login_required
def create_wanted():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    category = data.get('category', '其他')
    budget_min = data.get('budget_min', 0)
    budget_max = data.get('budget_max', 0)
    
    if not title:
        return jsonify({'code': 400, 'message': '标题不能为空'}), 400
    
    wanted = Wanted(
        user_id=g.current_user.id,
        title=title,
        description=description,
        category=category,
        budget_min=budget_min,
        budget_max=budget_max,
        status='求购中'
    )
    
    db.session.add(wanted)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': wanted.to_dict()
    })


@wanted_bp.route('/wanteds/<int:wanted_id>', methods=['PUT'])
@login_required
def update_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    
    if not wanted:
        return jsonify({'code': 404, 'message': '求购信息不存在'}), 404
    
    if wanted.user_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权修改'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        wanted.title = data['title']
    if 'description' in data:
        wanted.description = data['description']
    if 'category' in data:
        wanted.category = data['category']
    if 'budget_min' in data:
        wanted.budget_min = data['budget_min']
    if 'budget_max' in data:
        wanted.budget_max = data['budget_max']
    if 'status' in data:
        wanted.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '修改成功',
        'data': wanted.to_dict()
    })


@wanted_bp.route('/wanteds/<int:wanted_id>', methods=['DELETE'])
@login_required
def delete_wanted(wanted_id):
    wanted = Wanted.query.get(wanted_id)
    
    if not wanted:
        return jsonify({'code': 404, 'message': '求购信息不存在'}), 404
    
    if wanted.user_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权删除'}), 403
    
    WantedResponse.query.filter_by(wanted_id=wanted_id).delete()
    
    db.session.delete(wanted)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@wanted_bp.route('/wanteds/<int:wanted_id>/respond', methods=['POST'])
@login_required
def respond_to_wanted(wanted_id):
    data = request.get_json()
    product_id = data.get('product_id')
    message = data.get('message', '')
    
    wanted = Wanted.query.get(wanted_id)
    if not wanted:
        return jsonify({'code': 404, 'message': '求购信息不存在'}), 404
    
    if wanted.status != '求购中':
        return jsonify({'code': 400, 'message': '该求购已结束'}), 400
    
    if product_id:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'message': '商品不存在'}), 404
        
        if product.seller_id != g.current_user.id:
            return jsonify({'code': 403, 'message': '只能推荐自己的商品'}), 403
        
        if product.status != '上架':
            return jsonify({'code': 400, 'message': '商品已下架'}), 400
        
        existing = WantedResponse.query.filter_by(
            wanted_id=wanted_id,
            product_id=product_id
        ).first()
        if existing:
            return jsonify({'code': 400, 'message': '您已推荐过该商品'}), 400
    
    response = WantedResponse(
        wanted_id=wanted_id,
        product_id=product_id,
        responder_id=g.current_user.id,
        message=message
    )
    
    db.session.add(response)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '推荐成功',
        'data': response.to_dict()
    })


@wanted_bp.route('/wanteds/my', methods=['GET'])
@login_required
def get_my_wanteds():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    pagination = Wanted.query.filter_by(user_id=g.current_user.id).order_by(
        Wanted.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    wanteds = []
    for wanted in pagination.items:
        wanted_dict = wanted.to_dict()
        responses = WantedResponse.query.filter_by(wanted_id=wanted.id).all()
        wanted_dict['response_count'] = len(responses)
        wanteds.append(wanted_dict)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'wanteds': wanteds,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    })
