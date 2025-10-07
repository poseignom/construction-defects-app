from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect  # Добавляем импорт

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # Создаем экземпляр CSRF защиты

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = 'secret-key-12345-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///defects.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Инициализируем CSRF защиту
    
    login_manager.login_view = 'main.login'
    
    # Регистрация blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Инициализация security headers
    from app.security import init_security_headers
    init_security_headers(app)
    
    return app