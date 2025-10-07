from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_object(config_class)
    
    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'main.login'
    
    # Инициализация security headers
    from app.security import init_security_headers
    init_security_headers(app)
    
    # Регистрация blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app