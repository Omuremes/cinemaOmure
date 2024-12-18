from flask import Flask, request, jsonify,send_from_directory
import os
import json

app = Flask(__name__)

# Пути к файлам данных
UPLOAD_FOLDER = "/images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
USER_FILE = "users.json"
MOVIE_FILE = "movies.json"
SCHEDULE_FILE = "schedule.json"

# Функции работы с пользователями
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Функции работы с фильмами
def load_movies():
    if os.path.exists(MOVIE_FILE):
        with open(MOVIE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_movies(movies):
    with open(MOVIE_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, indent=4, ensure_ascii=False)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = load_users()
    if username in users:
        return jsonify({'success': False, 'message': 'Пользователь уже существует'}), 400

    users[username] = password
    save_users(users)
    return jsonify({'success': True, 'message': 'Регистрация успешна'}), 201

# Авторизация пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = load_users()
    if users.get(username) == password:
        return jsonify({'success': True, 'message': 'Вход выполнен'}), 200

    return jsonify({'success': False, 'message': 'Неверные данные'}), 401

# Получение списка фильмов
@app.route("/movies", methods=["GET"])
def get_movies():
    movies = load_movies()
    return jsonify(movies), 200

# Добавление нового фильма
@app.route("/movies", methods=["POST"])
def add_movie():
    data = request.json
    print("Полученные данные на сервере:", data)  # Отладка
    
    # Проверяем наличие ключей
    if not data or "title" not in data or "image_path" not in data:
        return jsonify({"error": "Invalid data"}), 400

    # Загружаем текущие фильмы
    movies = load_movies()
    
    # Добавляем новый фильм
    movies.append({"title": data["title"], "image_path": data["image_path"]})
    save_movies(movies)
    
    return jsonify({"message": "Movie added successfully"}), 201

@app.route("/schedule", methods=["POST"])
def add_schedule():
    """Добавление расписаний в schedule.json"""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Ожидается массив расписаний"}), 400

        new_schedules = []
        for entry in data:
            title = entry.get("title")
            date = entry.get("date")
            time = entry.get("time")
            price = entry.get("price")
            hall = entry.get("hall")

            if not title or not date or not price or not time or not hall:
                return jsonify({"error": "Все поля обязательны: title, date, time, hall"}), 400

            new_schedules.append(entry)

        # Загрузка и обновление файла schedule.json
        schedule_file = "schedule.json"
        if os.path.exists(schedule_file):
            with open(schedule_file, "r", encoding="utf-8") as file:
                schedules = json.load(file)
        else:
            schedules = []

        schedules.extend(new_schedules)

        with open(schedule_file, "w", encoding="utf-8") as file:
            json.dump(schedules, file, ensure_ascii=False, indent=4)

        return jsonify({"message": "Расписания успешно добавлены"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/schedules", methods=["GET"])
def get_schedules():
    """Получение всех расписаний"""
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            schedules = json.load(file)
        return jsonify(schedules), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/bookings", methods=["POST"])
def add_booking():
    """Добавление нового бронирования."""
    try:
        data = request.get_json()
        if not all(k in data for k in ["username", "movie_title", "hall", "date", "time", "seats"]):
            return jsonify({"error": "Поля username, movie_title, hall, date, time, seats обязательны"}), 400

        # Загрузка существующих бронирований
        if os.path.exists("bookings.json"):
            with open("bookings.json", "r", encoding="utf-8") as file:
                bookings = json.load(file)
        else:
            bookings = []

        # Добавление нового бронирования
        bookings.append(data)

        # Сохранение обновленных бронирований
        with open("bookings.json", "w", encoding="utf-8") as file:
            json.dump(bookings, file, ensure_ascii=False, indent=4)

        return jsonify({"message": "Booking added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/bookings", methods=["GET"])
def get_bookings():
    """Получение занятых мест для указанного фильма, зала, даты и времени."""
    movie_title = request.args.get("movie_title")
    hall = request.args.get("hall")
    date = request.args.get("date")
    time = request.args.get("time")

    try:
        if not all([movie_title, hall, date, time]):
            return jsonify({"error": "Параметры movie_title, hall, date, time обязательны"}), 400

        # Загрузка всех бронирований
        if os.path.exists("bookings.json"):
            with open("bookings.json", "r", encoding="utf-8") as file:
                bookings = json.load(file)
        else:
            bookings = []

        # Фильтруем бронирования по указанным параметрам
        occupied_seats = [
            seat for booking in bookings
            if booking["movie_title"] == movie_title and
               booking["hall"] == hall and
               booking["date"] == date and
               booking["time"] == time
            for seat in booking["seats"]
        ]

        return jsonify({"occupied_seats": occupied_seats}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/bookings_report", methods=["GET"])
def bookings_report():
    """Возвращает все данные о бронированиях для отчётности."""
    try:
        if os.path.exists("bookings.json"):
            with open("bookings.json", "r", encoding="utf-8") as file:
                bookings = json.load(file)
        else:
            bookings = []

        return jsonify(bookings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/user_history", methods=["GET"])
def user_history():
    """Возвращает историю бронирований всех пользователей."""
    try:
        if os.path.exists("bookings.json"):
            with open("bookings.json", "r", encoding="utf-8") as file:
                bookings = json.load(file)
        else:
            bookings = []

        return jsonify(bookings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Удаление фильма
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    movies = load_movies()
    if 0 <= movie_id < len(movies):
        deleted_movie = movies.pop(movie_id)
        save_movies(movies)
        return jsonify({'success': True, 'message': f"Фильм '{deleted_movie['title']}' удален"}), 200
    return jsonify({'success': False, 'message': 'Фильм не найден'}), 404

if __name__ == '__main__':
    app.run(debug=True)
