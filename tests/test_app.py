import pytest
import os
from app import create_app, db
from app.models import User, Defect

@pytest.fixture
def app():
    """Создаем тестовое приложение"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        # Создаем тестовых пользователей
        users = [
            User(username='test_manager', role='manager'),
            User(username='test_engineer', role='engineer'),
            User(username='test_leader', role='leader')
        ]
        for user in users:
            user.set_password('test123')
        db.session.add_all(users)
        db.session.commit()
        
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Тестовый runner для CLI команд"""
    return app.test_cli_runner()

class TestAuth:
    """Тесты аутентификации"""
    
    def test_login_success(self, client):
        """Тест успешного входа"""
        response = client.post('/login', data={
            'username': 'test_manager',
            'password': 'test123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Используем decode для работы с русскими символами
        assert 'Все дефекты' in response.data.decode('utf-8')
    
    def test_login_failure(self, client):
        """Тест неудачного входа"""
        response = client.post('/login', data={
            'username': 'test_manager',
            'password': 'wrong_password'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'Неверное имя пользователя или пароль' in response.data.decode('utf-8')
    
    def test_logout(self, client):
        """Тест выхода"""
        # Сначала логинимся
        client.post('/login', data={
            'username': 'test_manager',
            'password': 'test123'
        })
        # Затем выходим
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'Добро пожаловать' in response.data.decode('utf-8')

class TestDefects:
    """Тесты работы с дефектами"""
    
    def test_defects_page_requires_login(self, client):
        """Тест что страница дефектов требует авторизации"""
        response = client.get('/defects', follow_redirects=True)
        assert 'Вход в систему' in response.data.decode('utf-8')
    
    def test_add_defect_as_manager(self, client):
        """Тест добавления дефекта менеджером"""
        # Логинимся как менеджер
        client.post('/login', data={
            'username': 'test_manager',
            'password': 'test123'
        })
        
        # Добавляем дефект
        response = client.post('/add_defect', data={
            'title': 'Тестовый дефект',
            'description': 'Описание тестового дефекта',
            'priority': 'Высокий'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Дефект успешно добавлен' in response.data.decode('utf-8')
        assert 'Тестовый дефект' in response.data.decode('utf-8')
    
    def test_add_defect_permission_engineer(self, client):
        """Тест что инженер может добавлять дефекты"""
        client.post('/login', data={
            'username': 'test_engineer',
            'password': 'test123'
        })
        
        response = client.get('/add_defect')
        assert response.status_code == 200
    
    def test_add_defect_permission_leader(self, client):
        """Тест что руководитель НЕ может добавлять дефекты"""
        client.post('/login', data={
            'username': 'test_leader',
            'password': 'test123'
        })
        
        response = client.get('/add_defect', follow_redirects=True)
        assert response.status_code == 200
        assert 'У вас нет прав' in response.data.decode('utf-8')

class TestUserModel:
    """Тесты моделей пользователей"""
    
    def test_password_hashing(self, app):
        """Тест хэширования паролей"""
        with app.app_context():
            user = User.query.filter_by(username='test_manager').first()
            assert user.check_password('test123') is True
            assert user.check_password('wrong_password') is False
    
    def test_user_roles(self, app):
        """Тест ролей пользователей"""
        with app.app_context():
            manager = User.query.filter_by(username='test_manager').first()
            engineer = User.query.filter_by(username='test_engineer').first()
            leader = User.query.filter_by(username='test_leader').first()
            
            assert manager.role == 'manager'
            assert engineer.role == 'engineer'
            assert leader.role == 'leader'

def test_stats_page_leader_only(client):
    """Тест что статистика доступна только руководителю"""
    # Пробуем зайти как менеджер
    client.post('/login', data={
        'username': 'test_manager',
        'password': 'test123'
    })
    
    response = client.get('/stats', follow_redirects=True)
    assert 'Доступ запрещен' in response.data.decode('utf-8')
    
    # Пробуем зайти как руководитель
    client.get('/logout')
    client.post('/login', data={
        'username': 'test_leader',
        'password': 'test123'
    })
    
    response = client.get('/stats')
    assert response.status_code == 200
    assert 'Статистика дефектов' in response.data.decode('utf-8')

# Простые тесты без русских символов для надежности
def test_home_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Тест страницы логина"""
    response = client.get('/login')
    assert response.status_code == 200