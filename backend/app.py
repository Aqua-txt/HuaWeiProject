import os
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, Admin
from werkzeug.security import generate_password_hash


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {"origins": app.config['CORS_ORIGINS']},
        r"/admin/*": {"origins": app.config['CORS_ORIGINS']}
    })

    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.chat import chat_bp
    from routes.user import user_bp
    from routes.order import order_bp
    from routes.review import review_bp
    from routes.report import report_bp
    from routes.wanted import wanted_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(wanted_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        
        if not Admin.query.filter_by(username='admin').first():
            default_admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                nickname='系统管理员'
            )
            db.session.add(default_admin)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
