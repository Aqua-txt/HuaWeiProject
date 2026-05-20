from flask import Blueprint, request, jsonify, g, current_app
from models import db, Product
from utils.auth import login_required
from utils.images import save_image, allowed_image

user_bp = Blueprint('user', __name__)


@user_bp.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    nickname = request.form.get('nickname', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()

    if nickname:
        if len(nickname) > 50:
            return jsonify({'code': 400, 'message': '昵称长度不能超过50个字符'}), 400
        g.current_user.nickname = nickname

    if phone:
        g.current_user.phone = phone
    if email:
        g.current_user.email = email

    avatar_file = request.files.get('avatar')
    if avatar_file and avatar_file.filename:
        if not allowed_image(avatar_file.filename):
            return jsonify({'code': 400, 'message': '仅支持 png/jpg/jpeg/gif/webp 格式'}), 400
        g.current_user.avatar = save_image(avatar_file)

    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {'user': g.current_user.to_dict()}
    })


@user_bp.route('/api/user/products', methods=['GET'])
@login_required
def my_products():
    status = request.args.get('status', '')  # '' = all, '上架', '已下架'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Product.query.filter_by(seller_id=g.current_user.id)
    if status:
        query = query.filter(Product.status == status)
    query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = [p.to_dict() for p in pagination.items]

    return jsonify({
        'code': 200,
        'data': {
            'products': products,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })
