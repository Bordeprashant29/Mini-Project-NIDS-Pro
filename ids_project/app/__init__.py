from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from ids_project.config import Config
from .utils import load_pipeline

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()

pipeline = None

def create_app():
    global pipeline
    app = Flask(__name__)
    app.config.from_object(Config)

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    pipeline = load_pipeline(app.config["MODEL_PATH"])

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .dashboard.routes import dash_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dash_bp, url_prefix="/dashboard")

    return app
