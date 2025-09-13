from flask import Flask
from .config import Config
from .models import db

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)

    # register routes
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # create sqlite tables if missing
    with app.app_context():
        db.create_all()

    return app
