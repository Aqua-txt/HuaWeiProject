from datetime import datetime
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    images = db.Column(db.Text, default='[]')  # JSON array of image filenames
    status = db.Column(db.String(10), nullable=False, default='上架', index=True)  # 上架/已下架/已删除
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    favorites = db.relationship('Favorite', backref='product', lazy='dynamic')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname if self.seller else '',
            'seller_avatar': self.seller.avatar if self.seller else '',
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'condition': self.condition,
            'images': json.loads(self.images) if self.images else [],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Conversation(db.Model):
    __tablename__ = 'conversation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    msg_type = db.Column(db.String(10), default='text')  # text / image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='待支付')
    payment_method = db.Column(db.String(20), default='')
    transaction_id = db.Column(db.String(100), default='')
    refund_reason = db.Column(db.Text, default='')
    refund_status = db.Column(db.String(20), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='orders')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'order_no': self.order_no,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'product_images': json.loads(self.product.images) if self.product and self.product.images else [],
            'buyer_id': self.buyer_id,
            'buyer_nickname': self.buyer.nickname if self.buyer else '',
            'buyer_avatar': self.buyer.avatar if self.buyer else '',
            'seller_id': self.seller_id,
            'seller_nickname': self.seller.nickname if self.seller else '',
            'seller_avatar': self.seller.avatar if self.seller else '',
            'price': self.price,
            'status': self.status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'refund_reason': self.refund_reason,
            'refund_status': self.refund_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'refunded_at': self.refunded_at.isoformat() if self.refunded_at else None,
        }


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref='review')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id])
    reviewee = db.relationship('User', foreign_keys=[reviewee_id])

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_nickname': self.reviewer.nickname if self.reviewer else '',
            'reviewer_avatar': self.reviewer.avatar if self.reviewer else '',
            'reviewee_id': self.reviewee_id,
            'reviewee_nickname': self.reviewee.nickname if self.reviewee else '',
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(20), default='待处理')
    handler_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    handle_result = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime)

    product = db.relationship('Product', backref='reports')
    reporter = db.relationship('User', backref='reports')
    handler = db.relationship('Admin', backref='handled_reports')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'reporter_id': self.reporter_id,
            'reporter_nickname': self.reporter.nickname if self.reporter else '',
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'handler_id': self.handler_id,
            'handle_result': self.handle_result,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
        }


class Wanted(db.Model):
    __tablename__ = 'wanted'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    category = db.Column(db.String(20), nullable=False, default='其他')
    budget_min = db.Column(db.Float, default=0)
    budget_max = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='求购中')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='wanteds')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'user_avatar': self.user.avatar if self.user else '',
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class WantedResponse(db.Model):
    __tablename__ = 'wanted_response'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wanted_id = db.Column(db.Integer, db.ForeignKey('wanted.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    responder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wanted = db.relationship('Wanted', backref='responses')
    product = db.relationship('Product', backref='wanted_responses')
    responder = db.relationship('User', backref='wanted_responses')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'wanted_id': self.wanted_id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else '',
            'product_images': json.loads(self.product.images) if self.product and self.product.images else [],
            'product_price': self.product.price if self.product else 0,
            'responder_id': self.responder_id,
            'responder_nickname': self.responder.nickname if self.responder else '',
            'responder_avatar': self.responder.avatar if self.responder else '',
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
