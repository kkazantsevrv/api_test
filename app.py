from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с фронтенда

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    notes = db.relationship('Note', backref='user', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # user = db.relationship('User', backref=db.backref('notes', lazy=True))

with app.app_context():
    db.create_all()

# Регистрация пользователя
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Авторизация пользователя
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful", "user": {"id": user.id, "username": user.username}}), 200

# Личный кабинет (защищенный маршрут)
@app.route('/api/profile/<int:user_id>', methods=['GET'])
def api_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": {"id": user.id, "username": user.username}}), 200

@app.route('/api/profile/<int:user_id>', methods=['GET'])
def api_note_get(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": {"id": user.id, "notes": user.notes}}), 200
    

@app.route('/api/note', methods=['POST'])
def api_note():
    data=request.json
    # Проверяем, что данные переданы
    if not data or 'content' not in data or 'user_id' not in data:
        return jsonify({"error": "Content and user_id are required"}), 400
    
    content = data.get('content')
    user_id = data.get('user_id')
    # Проверяем, существует ли пользователь
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_note = Note(content=content, user_id=user_id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"message": "Note created successfully", "note": {"id": new_note.id, "content": new_note.content}}), 201

# Главная страница (фронтенд)
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)