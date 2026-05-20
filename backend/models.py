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
