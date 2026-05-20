import json
from flask import Blueprint, request, jsonify, g, current_app, send_from_directory
from models import db, Product, Favorite
from utils.auth import login_required, optional_login
from utils.images import save_image, allowed_image

products_bp = Blueprint('products', __name__)


@products_bp.route('/api/products', methods=['GET'])
@optional_login
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', '').strip()
    keyword = request.args.get('keyword', '').strip()
    sort = request.args.get('sort', 'latest')  # latest / price_asc / price_desc
    seller_id = request.args.get('seller_id', type=int)
    mine = request.args.get('mine', type=int)  # 1 = only current user's products

    query = Product.query.filter(Product.status == '上架')

    if category:
        query = query.filter(Product.category == category)
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(Product.title.like(like), Product.description.like(like))
        )
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    if mine and g.current_user:
        query = query.filter(Product.seller_id == g.current_user.id)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = [p.to_dict() for p in pagination.items]

    # If user logged in, mark favorites
    if g.current_user:
        product_ids = [p['id'] for p in products]
        favs = Favorite.query.filter(
            Favorite.user_id == g.current_user.id,
            Favorite.product_id.in_(product_ids)
        ).all()
        fav_ids = {f.product_id for f in favs}
        for p in products:
            p['is_favorited'] = p['id'] in fav_ids

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


@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
@optional_login
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404

    data = product.to_dict()
    if g.current_user:
        fav = Favorite.query.filter_by(
            user_id=g.current_user.id, product_id=product_id
        ).first()
        data['is_favorited'] = bool(fav)

    return jsonify({'code': 200, 'data': data})


@products_bp.route('/api/products', methods=['POST'])
@login_required
def create_product():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    price_str = request.form.get('price', '').strip()
    category = request.form.get('category', '其他').strip()
    condition = request.form.get('condition', '轻微使用痕迹').strip()
    image_files = request.files.getlist('images')

    if not title:
        return jsonify({'code': 400, 'message': '请输入商品标题'}), 400
    if len(title) > 100:
        return jsonify({'code': 400, 'message': '标题长度不能超过100个字符'}), 400

    try:
        price = float(price_str)
        if price < 0.01 or price > 99999.99:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'code': 400, 'message': '请输入有效价格（0.01-99999.99）'}), 400

    valid_categories = ['教材', '数码', '生活', '其他']
    if category not in valid_categories:
        category = '其他'

    valid_conditions = ['全新', '几乎全新', '轻微使用痕迹', '明显使用痕迹']
    if condition not in valid_conditions:
        condition = '轻微使用痕迹'

    if not image_files or all(not f.filename for f in image_files):
        return jsonify({'code': 400, 'message': '请至少上传一张图片'}), 400
    if len(image_files) > 6:
        return jsonify({'code': 400, 'message': '最多上传6张图片'}), 400

    image_names = []
    for f in image_files:
        if not f.filename:
            continue
        if not allowed_image(f.filename):
            return jsonify({'code': 400, 'message': '仅支持 png/jpg/jpeg/gif/webp 格式图片'}), 400
        image_names.append(save_image(f))

    product = Product(
        seller_id=g.current_user.id,
        title=title,
        description=description,
        price=price,
        category=category,
        condition=condition,
        images=json.dumps(image_names),
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '发布成功',
        'data': product.to_dict()
    })


@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    if product.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只能编辑自己的商品'}), 403

    title = request.form.get('title', '').strip()
    if title:
        if len(title) > 100:
            return jsonify({'code': 400, 'message': '标题长度不能超过100个字符'}), 400
        product.title = title

    description = request.form.get('description')
    if description is not None:
        product.description = description.strip()

    price_str = request.form.get('price')
    if price_str:
        try:
            price = float(price_str)
            if price < 0.01 or price > 99999.99:
                raise ValueError
            product.price = price
        except (ValueError, TypeError):
            return jsonify({'code': 400, 'message': '请输入有效价格'}), 400

    category = request.form.get('category')
    if category:
        if category in ['教材', '数码', '生活', '其他']:
            product.category = category

    condition = request.form.get('condition')
    if condition:
        if condition in ['全新', '几乎全新', '轻微使用痕迹', '明显使用痕迹']:
            product.condition = condition

    image_files = request.files.getlist('images')
    if image_files and any(f.filename for f in image_files):
        image_names = []
        for f in image_files:
            if not f.filename:
                continue
            if not allowed_image(f.filename):
                return jsonify({'code': 400, 'message': '仅支持 png/jpg/jpeg/gif/webp 格式图片'}), 400
            image_names.append(save_image(f))
        if image_names:
            product.images = json.dumps(image_names)

    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': product.to_dict()
    })


@products_bp.route('/api/products/<int:product_id>/status', methods=['PUT'])
@login_required
def update_product_status(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    if product.seller_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '只能操作自己的商品'}), 403

    data = request.get_json() or {}
    new_status = data.get('status', '')

    if new_status not in ['上架', '已下架']:
        return jsonify({'code': 400, 'message': '无效的状态'}), 400

    product.status = new_status
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '操作成功',
        'data': product.to_dict()
    })


@products_bp.route('/api/products/<int:product_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404

    fav = Favorite.query.filter_by(
        user_id=g.current_user.id, product_id=product_id
    ).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'code': 200, 'message': '已取消收藏', 'data': {'is_favorited': False}})
    else:
        fav = Favorite(user_id=g.current_user.id, product_id=product_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({'code': 200, 'message': '收藏成功', 'data': {'is_favorited': True}})


@products_bp.route('/api/favorites', methods=['GET'])
@login_required
def my_favorites():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Favorite.query.filter_by(user_id=g.current_user.id).order_by(
        Favorite.created_at.desc()
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for fav in pagination.items:
        p = fav.product
        if p:
            item = p.to_dict()
            item['is_favorited'] = True
            item['favorited_at'] = fav.created_at.isoformat() if fav.created_at else None
            items.append(item)

    return jsonify({
        'code': 200,
        'data': {
            'products': items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@products_bp.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
