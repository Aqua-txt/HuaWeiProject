from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Report, Product
from utils.auth import login_required

report_bp = Blueprint('report', __name__)


@report_bp.route('/api/reports', methods=['POST'])
@login_required
def create_report():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    report_type = data.get('report_type', '').strip()
    description = data.get('description', '').strip()

    if not product_id:
        return jsonify({'code': 400, 'message': '缺少商品ID'}), 400
    if not report_type:
        return jsonify({'code': 400, 'message': '请选择举报类型'}), 400
    if len(description) < 10:
        return jsonify({'code': 400, 'message': '举报描述至少10个字'}), 400

    valid_types = ['虚假信息', '违规商品', '诈骗行为', '其他']
    if report_type not in valid_types:
        return jsonify({'code': 400, 'message': '无效的举报类型'}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({'code': 404, 'message': '商品不存在'}), 404

    existing = Report.query.filter_by(
        reporter_id=g.current_user.id,
        product_id=product_id
    ).first()
    if existing:
        return jsonify({'code': 400, 'message': '你已举报过该商品'}), 400

    report = Report(
        reporter_id=g.current_user.id,
        product_id=product_id,
        report_type=report_type,
        description=description,
        status='待处理',
    )
    db.session.add(report)

    product.report_count = (product.report_count or 0) + 1
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '举报提交成功',
        'data': report.to_dict()
    })


@report_bp.route('/api/reports', methods=['GET'])
@login_required
def list_reports():
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Report.query.filter_by(reporter_id=g.current_user.id)

    if status:
        query = query.filter(Report.status == status)

    query = query.order_by(Report.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'reports': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
        }
    })


@report_bp.route('/api/reports/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '举报不存在'}), 404
    if report.reporter_id != g.current_user.id:
        return jsonify({'code': 403, 'message': '无权查看'}), 403

    return jsonify({'code': 200, 'data': report.to_dict()})
