from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
import os
import requests  # Импорт для Flask-запросов

class SeatSelection(QWidget):
    BASE_URL = "https://omuremes.pythonanywhere.com/bookings"  # URL вашего Flask-сервера

    def __init__(self, username, movie_title, hall, date, time):
        super().__init__()
        self.username = username
        self.movie_title = movie_title
        self.hall = hall
        self.date = date
        self.time = time
        self.selected_seats = []
        self.occupied_seats = self.load_occupied_seats()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Выбор мест")
        self.setFixedSize(600, 600)
        self.setStyleSheet("background-color: #2e2e2e;")

        main_layout = QVBoxLayout()

        # Заголовок с информацией
        title_label = QLabel(f"Фильм: {self.movie_title}\nЗал: {self.hall}\nДата: {self.date}, Время: {self.time}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Легенда
        legend_layout = QHBoxLayout()

        available_label = QLabel("Наши места")
        available_label.setFont(QFont("Arial", 10))
        available_label.setStyleSheet("color: white;")
        legend_layout.addWidget(available_label)

        available_indicator = QPushButton()
        available_indicator.setFixedSize(20, 20)
        available_indicator.setStyleSheet("background-color: green; border: none;")
        legend_layout.addWidget(available_indicator)

        occupied_label = QLabel("Занято")
        occupied_label.setFont(QFont("Arial", 10))
        occupied_label.setStyleSheet("color: white;")
        legend_layout.addWidget(occupied_label)

        occupied_indicator = QPushButton()
        occupied_indicator.setFixedSize(20, 20)
        occupied_indicator.setStyleSheet("background-color: red; border: none;")
        legend_layout.addWidget(occupied_indicator)

        main_layout.addLayout(legend_layout)

        # Сетка мест
        self.seat_layout = QVBoxLayout()
        seat_number = 1
        for row in range(6):  # 6 рядов
            row_layout = QHBoxLayout()
            for col in range(6):  # 6 мест в ряду
                seat_button = QPushButton(str(seat_number))
                seat_button.setFixedSize(50, 50)
                seat_button.setStyleSheet(self.get_seat_style(seat_number))
                seat_button.clicked.connect(lambda _, num=seat_number: self.toggle_seat(num))
                row_layout.addWidget(seat_button)
                seat_number += 1
            self.seat_layout.addLayout(row_layout)

        main_layout.addLayout(self.seat_layout)

        # Выбранное место
        self.selected_seat_label = QLabel("Ряд: , место: ")
        self.selected_seat_label.setFont(QFont("Arial", 12))
        self.selected_seat_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.selected_seat_label, alignment=Qt.AlignCenter)

        # Кнопка "Купить"
        buy_button = QPushButton("Купить")
        buy_button.setFixedSize(100, 50)
        buy_button.setStyleSheet("background-color: green; color: white; font-size: 16px; border-radius: 10px;")
        buy_button.clicked.connect(self.confirm_booking)
        main_layout.addWidget(buy_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def load_occupied_seats(self):
        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "movie_title": self.movie_title,
                    "hall": self.hall,
                    "date": self.date,
                    "time": self.time,
                },
            )
            if response.status_code == 200:
                return response.json().get("occupied_seats", [])
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить занятые места.")
                return []
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")
            return []

    def get_seat_style(self, seat_number):
        if seat_number in self.occupied_seats:
            return "background-color: red; border: none; color: white; font-weight: bold;"
        return "background-color: white; border: none; color: black; font-weight: bold;"

    def toggle_seat(self, seat_number):
        if seat_number in self.occupied_seats:
            return

        if seat_number in self.selected_seats:
            self.selected_seats.remove(seat_number)
        else:
            self.selected_seats.append(seat_number)

        self.selected_seat_label.setText(f"Выбрано мест: {', '.join(map(str, self.selected_seats))}")
        self.update_seat_styles()

    def update_seat_styles(self):
        seat_number = 1
        for row in range(self.seat_layout.count()):
            row_layout = self.seat_layout.itemAt(row)
            for col in range(row_layout.count()):
                button = row_layout.itemAt(col).widget()
                if button:
                    button.setStyleSheet(self.get_seat_style(seat_number))
                    seat_number += 1

    def confirm_booking(self):
        if not self.selected_seats:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одно место.")
            return

        booking = {
            "username": self.username,
            "movie_title": self.movie_title,
            "hall": self.hall,
            "date": self.date,
            "time": self.time,
            "seats": self.selected_seats,
        }

        try:
            response = requests.post(self.BASE_URL, json=booking)
            if response.status_code == 201:
                QMessageBox.information(self, "Успех", "Места успешно забронированы.")
                self.close()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить бронирование.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к серверу: {e}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = SeatSelection(username="test_user", movie_title="Фильм", hall="ЗАЛ 1", date="01.01.2025", time="18:00")
    window.show()
    sys.exit(app.exec_())
