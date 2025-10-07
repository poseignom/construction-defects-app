from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'engineer', 'manager', 'leader'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Defect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='Средний')  # Низкий, Средний, Высокий
    status = db.Column(db.String(20), default='Новая')  # Новая, В работе, На проверке, Закрыта
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Связи
    author = db.relationship('User', foreign_keys=[author_id], backref='created_defects')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_defects')
    
    def __repr__(self):
        return f'<Defect {self.title}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
