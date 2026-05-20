from datetime import datetime
from flask import Blueprint, request, jsonify, g
from models import db, Conversation, Message
from utils.auth import login_required

chat_bp = Blueprint('chat', __name__)


def _other_user_id(conv):
    """Return the other participant's user id for the current user."""
    return conv.seller_id if g.current_user.id == conv.buyer_id else conv.buyer_id


@chat_bp.route('/api/conversations', methods=['GET'])
@login_required
def list_conversations():
    convs = Conversation.query.filter(
        db.or_(
            Conversation.buyer_id == g.current_user.id,
            Conversation.seller_id == g.current_user.id,
        )
    ).order_by(Conversation.updated_at.desc()).all()

    result = []
    for c in convs:
        data = c.to_dict()
        last_msg = c.messages.order_by(Message.created_at.desc()).first()
        data['last_message'] = last_msg.to_dict() if last_msg else None
        unread = c.messages.filter(
            Message.sender_id != g.current_user.id,
            Message.is_read == False
        ).count()
        data['unread_count'] = unread
        result.append(data)

    return jsonify({'code': 200, 'data': {'conversations': result}})


@chat_bp.route('/api/conversations', methods=['POST'])
@login_required
def create_conversation():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    seller_id = data.get('seller_id')

    if not product_id or not seller_id:
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    seller_id = int(seller_id)
    product_id = int(product_id)

    if seller_id == g.current_user.id:
        return jsonify({'code': 400, 'message': '不能和自己聊天'}), 400

    existing = Conversation.query.filter_by(
        product_id=product_id,
        buyer_id=g.current_user.id,
        seller_id=seller_id,
    ).first()

    if existing:
        return jsonify({'code': 200, 'data': existing.to_dict()})

    conv = Conversation(
        product_id=product_id,
        buyer_id=g.current_user.id,
        seller_id=seller_id,
    )
    db.session.add(conv)
    db.session.commit()

    return jsonify({'code': 200, 'data': conv.to_dict()})


@chat_bp.route('/api/conversations/<int:conv_id>/messages', methods=['GET'])
@login_required
def get_messages(conv_id):
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({'code': 404, 'message': '会话不存在'}), 404
    if g.current_user.id not in [conv.buyer_id, conv.seller_id]:
        return jsonify({'code': 403, 'message': '无权查看'}), 403

    # after_id: only fetch messages newer than this id (for polling)
    after_id = request.args.get('after_id', type=int)

    query = conv.messages
    if after_id:
        query = query.filter(Message.id > after_id)

    msgs = query.order_by(Message.created_at.asc()).all()

    # Mark the other party's messages as read
    other_id = _other_user_id(conv)
    unread = Message.query.filter_by(
        conversation_id=conv_id,
        sender_id=other_id,
        is_read=False,
    ).all()
    for m in unread:
        m.is_read = True
    if unread:
        db.session.commit()

    return jsonify({
        'code': 200,
        'data': {
            'messages': [m.to_dict() for m in msgs],
        }
    })


@chat_bp.route('/api/conversations/<int:conv_id>/messages', methods=['POST'])
@login_required
def send_message(conv_id):
    conv = Conversation.query.get(conv_id)
    if not conv:
        return jsonify({'code': 404, 'message': '会话不存在'}), 404
    if g.current_user.id not in [conv.buyer_id, conv.seller_id]:
        return jsonify({'code': 403, 'message': '无权操作'}), 403

    data = request.get_json() or {}
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'code': 400, 'message': '消息不能为空'}), 400

    msg = Message(
        conversation_id=conv_id,
        sender_id=g.current_user.id,
        content=content,
        msg_type='text',
    )
    db.session.add(msg)
    conv.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'code': 200, 'data': msg.to_dict()})


@chat_bp.route('/api/unread-count', methods=['GET'])
@login_required
def unread_count():
    count = Message.query.join(Conversation).filter(
        db.or_(
            Conversation.buyer_id == g.current_user.id,
            Conversation.seller_id == g.current_user.id,
        ),
        Message.sender_id != g.current_user.id,
        Message.is_read == False,
    ).count()

    return jsonify({'code': 200, 'data': {'count': count}})
