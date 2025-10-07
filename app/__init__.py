from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = 'secret-key-12345'  # В реальном проекте нужно использовать сложный ключ
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///defects.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений с приложением
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    # Регистрация blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
