import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # Database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'nids.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "bordepratik32@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "ktczlrnczymijiyw")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # Paths
    MODEL_PATH = os.path.join(BASE_DIR, "model", "nids_pipeline.pkl")
    USERS_FILE = os.path.join(BASE_DIR, "users.json")
