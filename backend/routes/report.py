from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Report, Product
from utils.auth import login_required

report_bp = Blueprint('report', __name__, url_prefix='/api')


@report_bp.route('/reports', methods=['POST'])
@login_required
def create_report():
    data = request.get_json()
    product_id = data.get('product_id')
    reason = data.get('reason') or data.get('report_type')
    description = data.get('description', '')
    
    if not product_id or not reason:
        return jsonify({'code': 400, 'message': '缺少必要参数'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404
    
    if product.seller_id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能举报自己的商品'}), 400
    
    existing_report = Report.query.filter_by(
        product_id=product_id,
        reporter_id=g.current_user.id
    ).first()
    if existing_report:
        return jsonify({'code': 400, 'message': '您已举报过该商品'}), 400
    
    report = Report(
        product_id=product_id,
        reporter_id=g.current_user.id,
        reason=reason,
        description=description
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '举报成功，我们会尽快处理',
        'data': report.to_dict()
    })


@report_bp.route('/reports/check/<int:product_id>', methods=['GET'])
@login_required
def check_reported(product_id):
    report = Report.query.filter_by(
        product_id=product_id,
        reporter_id=g.current_user.id
    ).first()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'reported': report is not None
        }
    })
