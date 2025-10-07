from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db
from app.models import User, Defect

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.defects'))
        else:
            flash('Неверное имя пользователя или пароль.')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/defects')
@login_required
def defects():
    defects_list = Defect.query.all()
    return render_template('defects.html', defects=defects_list)

@main.route('/add_defect', methods=['GET', 'POST'])
@login_required
def add_defect():
    # Только инженер и менеджер могут добавлять дефекты
    if current_user.role not in ['engineer', 'manager']:
        flash('У вас нет прав для добавления дефектов.')
        return redirect(url_for('main.defects'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')
        
        new_defect = Defect(
            title=title,
            description=description,
            priority=priority,
            author_id=current_user.id
        )
        
        # Если пользователь менеджер, он может назначить исполнителя
        if current_user.role == 'manager':
            assigned_username = request.form.get('assigned_to')
            if assigned_username:
                assigned_user = User.query.filter_by(username=assigned_username, role='engineer').first()
                if assigned_user:
                    new_defect.assigned_to_id = assigned_user.id
        
        db.session.add(new_defect)
        db.session.commit()
        flash('Дефект успешно добавлен!')
        return redirect(url_for('main.defects'))
    
    # Для менеджера получаем список инженеров для назначения
    engineers = User.query.filter_by(role='engineer').all() if current_user.role == 'manager' else []
    return render_template('add_defect.html', engineers=engineers)

@main.route('/update_status/<int:defect_id>/<new_status>')
@login_required
def update_status(defect_id, new_status):
    defect = Defect.query.get_or_404(defect_id)
    
    # Проверяем права: автор или назначенный исполнитель могут менять статус
    if current_user.id == defect.author_id or current_user.id == defect.assigned_to_id:
        defect.status = new_status
        db.session.commit()
        flash('Статус обновлен.')
    else:
        flash('У вас нет прав для изменения этого дефекта.')
    
    return redirect(url_for('main.defects'))

# Обработчик для создания тестовых пользователей, если их нет
@main.before_app_request
def create_test_users():
    if not User.query.filter_by(username='manager').first():
        # Создаем тестовых пользователей
        users_data = [
            {'username': 'manager', 'password': 'manager123', 'role': 'manager'},
            {'username': 'engineer', 'password': 'engineer123', 'role': 'engineer'},
            {'username': 'leader', 'password': 'leader123', 'role': 'leader'}
        ]
        
        for user_data in users_data:
            user = User(username=user_data['username'], role=user_data['role'])
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()