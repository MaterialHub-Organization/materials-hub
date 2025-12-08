import os
import secrets


class ConfigManager:
    def __init__(self, app):
        self.app = app

    def load_config(self, config_name=None):
        # Determina el entorno
        if config_name is None:
            config_name = os.getenv("FLASK_ENV", "development")

        # Carga la configuración correspondiente
        if config_name == "testing":
            self.app.config.from_object(TestingConfig)
        elif config_name == "production":
            self.app.config.from_object(ProductionConfig)
        else:
            self.app.config.from_object(DevelopmentConfig)

        # Aseguramos que la app tenga la SECRET_KEY
        if not self.app.secret_key:
            self.app.secret_key = self.app.config.get("SECRET_KEY")


class Config:
    # Secret key
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Config generales
    TIMEZONE = "Europe/Madrid"
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = "uploads"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'default_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'default_password')}@"
        f"{os.getenv('POSTGRES_HOSTNAME', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DATABASE', 'default_db')}"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'materialhub_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'materialhub_password')}@"
        f"{os.getenv('POSTGRES_HOSTNAME', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DATABASE', 'materialhub')}"
    )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'materialhub_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'materialhub_password')}@"
        f"{os.getenv('POSTGRES_HOSTNAME', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_TEST_DATABASE', 'materialhub_test')}"
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
