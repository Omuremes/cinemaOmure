from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QMessageBox, QTableWidget, QTableWidgetItem
from changeMovie import ChangeMovieWindow
import requests

class AdminPanel(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setFixedSize(600, 400)
        self.username = username
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel(f"Добро пожаловать, {self.username}!")
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(welcome_label)

        # Кнопка "Добавить фильм"
        self.add_button = QPushButton("Добавить фильм")
        self.add_button.setFixedSize(150, 50)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.add_button.clicked.connect(self.open_change_movie_window)
        layout.addWidget(self.add_button)

        # Кнопка "Отчётность"
        self.report_button = QPushButton("Отчётность")
        self.report_button.setFixedSize(150, 50)
        self.report_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.report_button.clicked.connect(self.show_report)
        layout.addWidget(self.report_button)

        # Кнопка "История пользователей"
        self.history_button = QPushButton("История пользователей")
        self.history_button.setFixedSize(200, 50)
        self.history_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.history_button.clicked.connect(self.show_user_history)
        layout.addWidget(self.history_button)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def open_change_movie_window(self):
        self.change_window = ChangeMovieWindow()
        self.change_window.show()

    def show_report(self):
        try:
            # Отправляем запрос к серверу Flask
            response = requests.get("https://omuremes.pythonanywhere.com/bookings_report")
            if response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить отчётность с сервера.")
                return

            # Получаем данные отчёта
            bookings = response.json()

            # Подсчёт продаж по фильмам и датам
            report_data = {}
            for booking in bookings:
                movie_title = booking["movie_title"]
                date = booking["date"]
                seats_sold = len(booking["seats"])
                hall = booking["hall"]
                price_per_seat = self.get_price_for_hall_and_time(hall, booking["time"])

                key = (movie_title, date)  # Уникальный ключ для фильма и даты
                if key not in report_data:
                    report_data[key] = {"tickets_sold": 0, "total_earnings": 0, "date": date}

                report_data[key]["tickets_sold"] += seats_sold
                report_data[key]["total_earnings"] += seats_sold * price_per_seat

            # Отображение отчёта
            self.display_report(report_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке отчётности: {e}")

    def show_user_history(self):
        try:
            # Отправляем GET-запрос на сервер
            response = requests.get("https://omuremes.pythonanywhere.com/user_history")
            if response.status_code != 200:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить историю пользователей.")
                return

            user_history = response.json()

            self.history_widget = QWidget()  # Сохраняем в атрибуте класса
            history_layout = QVBoxLayout()

            table = QTableWidget()
            table.setRowCount(len(user_history))
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Пользователь", "Фильм", "Зал", "Дата", "Места"])

            for row, booking in enumerate(user_history):
                table.setItem(row, 0, QTableWidgetItem(booking["username"]))
                table.setItem(row, 1, QTableWidgetItem(booking["movie_title"]))
                table.setItem(row, 2, QTableWidgetItem(booking["hall"]))
                table.setItem(row, 3, QTableWidgetItem(booking["date"]))
                table.setItem(row, 4, QTableWidgetItem(", ".join(map(str, booking["seats"]))))

            history_layout.addWidget(table)
            self.history_widget.setLayout(history_layout)
            self.history_widget.setWindowTitle("История пользователей")
            self.history_widget.setGeometry(200, 200, 800, 400)
            self.history_widget.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке истории: {e}")



    def get_price_for_hall_and_time(self, hall, time):
        # Предположим, что цена зависит от времени:
        time_prices = {
            "10:00": 280,
            "12:00": 320,
            "14:00": 400,
            "16:00": 420,
            "18:00": 500,
            "20:00": 560,
            "22:00": 600,
        }
        return time_prices.get(time, 400)  # По умолчанию 400

    def display_report(self, report_data):
        self.report_widget = QWidget()  # Сохраняем объект в атрибуте класса
        report_layout = QVBoxLayout()

        table = QTableWidget()
        table.setRowCount(len(report_data))
        table.setColumnCount(4)  # Увеличиваем количество столбцов до 4
        table.setHorizontalHeaderLabels(["Фильм", "Дата", "Продано билетов", "Доход (сом)"])

        for row, ((movie_title, date), data) in enumerate(report_data.items()):
            # Используем movie_title и date отдельно
            table.setItem(row, 0, QTableWidgetItem(movie_title))  # Название фильма
            table.setItem(row, 1, QTableWidgetItem(date))  # Дата
            table.setItem(row, 2, QTableWidgetItem(str(data["tickets_sold"])))  # Продано билетов
            table.setItem(row, 3, QTableWidgetItem(str(data["total_earnings"])))  # Доход

        report_layout.addWidget(table)
        self.report_widget.setLayout(report_layout)
        self.report_widget.setWindowTitle("Отчётность")
        self.report_widget.setGeometry(200, 200, 600, 400)
        self.report_widget.show()
