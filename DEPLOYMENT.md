# 🚀 Руководство по развертыванию

Это руководство поможет развернуть приложение на продакшен-сервере.

## 📋 Предварительные требования

- Python 3.8 или выше
- Доступ к серверу (VPS, облачный хостинг)
- База данных (SQLite для тестирования, PostgreSQL для продакшена)

## 🛠 Локальное развертывание (для тестирования)

### 1. Настройка окружения
```bash
# Клонируй репозиторий
git clone https://github.com/your-username/construction-defects-app.git
cd construction-defects-app

# Создай виртуальное окружение
python -m venv venv

# Активируй окружение
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Установи зависимости
pip install -r requirements.txt