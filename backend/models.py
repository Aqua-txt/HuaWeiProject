from datetime import datetime, timezone, timedelta

_beijing_tz = timezone(timedelta(hours=8))

def beijing_now():
    """Return naive datetime in Beijing time (for database storage)."""
    return datetime.now(_beijing_tz).replace(tzinfo=None)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255), default='')
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), default='')
    email = db.Column(db.String(100), default='')
    credit_score = db.Column(db.Float, default=0.0)
    credit_count = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=beijing_now)

    products = db.relationship('Product', backref='seller', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'phone': self.phone,
            'email': self.email,
            'credit_score': round(self.credit_score, 2) if self.credit_score else 0,
            'credit_count': self.credit_count,
            'is_banned': self.is_banned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False, default='其他', index=True)
    condition = db.Column(db.String(20), nullable=False, default='轻微使用痕迹')
    images = db.Column(db.Text, default='[]')
    status = db.Column(db.String(10), nullable=False, default='上架', index=True)
    wanted_id = db.Column(db.Integer, db.ForeignKey('wanted.id'), nullable=True)
    report_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=beijing_now)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now)

    favorites = db.relationship('Favorite', backref='product', lazy='dynamic')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname if self.seller else '',
            'seller_avatar': self.seller.avatar if self.seller else '',
            'seller_credit_score': round(self.seller.credit_score, 2) if self.seller and self.seller.credit_score else 0,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'condition': self.condition,
            'images': json.loads(self.images) if self.images else [],
            'status': self.status,
            'report_count': self.report_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Conversation(db.Model):
    __tablename__ = 'conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=beijing_now)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now)

    product = db.relationship('Product', backref='conversations')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])
    messages = db.relationship('Message', backref='conversation', lazy='dynamic',
                               order_by='Message.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'product_images': (__import__('json').loads(self.product.images)[0]
                               if self.product and self.product.images else ''),
            'buyer_id': self.buyer_id,
            'buyer_nickname': self.buyer.nickname if self.buyer else '',
            'buyer_avatar': self.buyer.avatar if self.buyer else '',
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname if self.seller else '',
            'seller_avatar': self.seller.avatar if self.seller else '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    msg_type = db.Column(db.String(10), default='text')
    created_at = db.Column(db.DateTime, default=beijing_now)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender_nickname': self.sender.nickname if self.sender else '',
            'sender_avatar': self.sender.avatar if self.sender else '',
            'content': self.content,
            'msg_type': self.msg_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read,
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=beijing_now)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id', name='uq_user_product_favorite'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='待付款', index=True)
    refund_reason = db.Column(db.Text, default='')
    refund_status = db.Column(db.String(20), default='')
    buyer_confirmed_at = db.Column(db.DateTime, nullable=True)
    seller_confirmed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=beijing_now)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now)

    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])
    product = db.relationship('Product', backref='orders')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'order_no': self.order_no,
            'buyer_id': self.buyer_id,
            'buyer_nickname': self.buyer.nickname if self.buyer else '',
            'buyer_avatar': self.buyer.avatar if self.buyer else '',
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname if self.seller else '',
            'seller_avatar': self.seller.avatar if self.seller else '',
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'product_images': json.loads(self.product.images) if self.product and self.product.images else [],
            'product_price': self.product.price if self.product else 0,
            'amount': self.amount,
            'status': self.status,
            'refund_reason': self.refund_reason,
            'refund_status': self.refund_status,
            'buyer_confirmed_at': self.buyer_confirmed_at.isoformat() if self.buyer_confirmed_at else None,
            'seller_confirmed_at': self.seller_confirmed_at.isoformat() if self.seller_confirmed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='待支付')
    pay_type = db.Column(db.String(20), default='wechat')
    created_at = db.Column(db.DateTime, default=beijing_now)

    order = db.relationship('Order', backref='payments')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'pay_type': self.pay_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    communication_score = db.Column(db.Integer, nullable=False)
    description_score = db.Column(db.Integer, nullable=False)
    speed_score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=beijing_now)

    order = db.relationship('Order', backref='reviews')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])

    __table_args__ = (
        db.UniqueConstraint('order_id', 'reviewer_id', name='uq_order_reviewer'),
    )

    def to_dict(self):
        overall = round(self.communication_score * 0.2 + self.description_score * 0.5 + self.speed_score * 0.3, 2)
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_no': self.order.order_no if self.order else '',
            'reviewer_id': self.reviewer_id,
            'reviewer_nickname': self.reviewer.nickname if self.reviewer else '',
            'reviewer_avatar': self.reviewer.avatar if self.reviewer else '',
            'reviewee_id': self.reviewee_id,
            'reviewee_nickname': self.reviewee.nickname if self.reviewee else '',
            'communication_score': self.communication_score,
            'description_score': self.description_score,
            'speed_score': self.speed_score,
            'overall_score': overall,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False, index=True)
    report_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='待处理', index=True)
    handler_note = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=beijing_now)
    handled_at = db.Column(db.DateTime, nullable=True)

    reporter = db.relationship('User', backref='reports')
    product = db.relationship('Product', backref='reports')

    __table_args__ = (
        db.UniqueConstraint('reporter_id', 'product_id', name='uq_reporter_product'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reporter_nickname': self.reporter.nickname if self.reporter else '',
            'reporter_student_id': self.reporter.student_id if self.reporter else '',
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'product_seller_id': self.product.seller_id if self.product else None,
            'product_seller_nickname': self.product.seller.nickname if self.product and self.product.seller else '',
            'report_type': self.report_type,
            'description': self.description,
            'status': self.status,
            'handler_note': self.handler_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
        }


class Wanted(db.Model):
    __tablename__ = 'wanted'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    budget_min = db.Column(db.Float, default=0)
    budget_max = db.Column(db.Float, default=99999.99)
    category = db.Column(db.String(20), nullable=False, default='其他', index=True)
    desired_condition = db.Column(db.String(20), default='')
    status = db.Column(db.String(20), nullable=False, default='进行中', index=True)
    created_at = db.Column(db.DateTime, default=beijing_now)
    updated_at = db.Column(db.DateTime, default=beijing_now, onupdate=beijing_now)

    user = db.relationship('User', backref='wanteds')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'user_avatar': self.user.avatar if self.user else '',
            'title': self.title,
            'description': self.description,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'category': self.category,
            'desired_condition': self.desired_condition,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WantedResponse(db.Model):
    __tablename__ = 'wanted_response'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wanted_id = db.Column(db.Integer, db.ForeignKey('wanted.id'), nullable=False, index=True)
    responder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price_offer = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, default='')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=beijing_now)

    wanted = db.relationship('Wanted', backref='responses')
    responder = db.relationship('User', backref='wanted_responses')
    product = db.relationship('Product', backref='wanted_responses')

    def to_dict(self):
        return {
            'id': self.id,
            'wanted_id': self.wanted_id,
            'responder_id': self.responder_id,
            'responder_nickname': self.responder.nickname if self.responder else '',
            'responder_avatar': self.responder.avatar if self.responder else '',
            'price_offer': self.price_offer,
            'message': self.message,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=beijing_now)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
