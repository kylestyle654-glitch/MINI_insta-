from flask import Flask
from .config import Config
from .extensions import db, jwt
from .errors import register_error_handlers

# import models to register with SQLAlchemy
from .models import user, post, media, like, comment  # noqa: F401

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    register_error_handlers(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.posts import posts_bp
    from .routes.media import media_bp
    from .routes.likes import likes_bp
    from .routes.comments import comments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(likes_bp)
    app.register_blueprint(comments_bp)

    with app.app_context():
        db.create_all()

    return app
