from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,QApplication,QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os,sys,requests
from seats import SeatSelection

class MovieSchedule(QMainWindow):
    def __init__(self, image_path, title,username):
        super().__init__()
        self.setWindowTitle("Расписание фильма")
        self.setStyleSheet("background-color: black;")
        self.setGeometry(100, 100, 900, 500)
        self.image_path = image_path
        self.username = username
        self.title = title
        self.initUI()

    def initUI(self):
        # Главное центральное виджет
        central_widget = QWidget()
        self.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)

        # Основной вертикальный макет
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Верхняя часть: кнопка назад и название фильма
        header_layout = QHBoxLayout()

        back_button = QPushButton("<")
        back_button.setFixedSize(40, 40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #000;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        back_button.clicked.connect(self.close)

        movie_title = QLabel(self.title)
        movie_title.setFont(QFont("Arial", 16, QFont.Bold))
        movie_title.setAlignment(Qt.AlignCenter)
        movie_title.setStyleSheet("""
                QLabel {
                    font-color: white;
                    color: white;
                }
            """)

        header_layout.addWidget(back_button, alignment=Qt.AlignLeft)
        header_layout.addWidget(movie_title, alignment=Qt.AlignCenter)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Изображение фильма
        movie_image = QLabel()
        pixmap = QPixmap(self.image_path).scaled(1000, 500, Qt.KeepAspectRatio)
        movie_image.setPixmap(pixmap)
        movie_image.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(movie_image)

        # Блок с датами
        self.date_layout = QHBoxLayout()  # Создаём макет для кнопок выбора даты
        dates = self.get_dates_from_schedule()  # Получаем список доступных дат

        for date in dates:  # Используем локальную переменную dates
            date_button = QPushButton(date)
            date_button.setCheckable(True)
            date_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #000;
                    border-radius: 10px;
                    font-size: 12px;
                    height: 25px;
                    width: 10px;
                }
                QPushButton:checked {
                    background-color: #00ff00;
                    color: white;
                }
            """)
            self.date_layout.addWidget(date_button)

        # Добавляем макет выбора дат в основной макет
        main_layout.addLayout(self.date_layout)

        # Сетка для залов и сеансов
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        halls, times, prices = self.get_schedule_data()

        for row, hall in enumerate(halls):
            hall_button = QPushButton(hall)
            hall_button.setFixedSize(70, 40)
            hall_button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #000;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d3d3d3;
                }
            """)
            grid_layout.addWidget(hall_button, row + 1, 0)

            for col, time in enumerate(times):
                time_button = QPushButton(f"{time}\n{prices[col % len(prices)]}")
                time_button.setFixedSize(70, 40)
                time_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #000;
                        border-radius: 10px;
                        font-size: 10px;
                        font-weight: bold;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #00ff00;
                    }
                """)
                time_button.clicked.connect(
                    lambda _, h=hall, t=time, p=prices[col % len(prices)], d=self.get_selected_date(): self.open_seat_selection(h, d, t, p)
                )
                grid_layout.addWidget(time_button, row + 1, col + 1)

        main_layout.addLayout(grid_layout)

    def get_dates_from_schedule(self):
        try:
            response = requests.get("https://omuremes.pythonanywhere.com/schedules")
            if response.status_code == 200:
                schedules = response.json()
                dates = list({entry['date'] for entry in schedules if entry['title'] == self.title})
                return sorted(dates)
            else:
                print(f"Ошибка запроса: {response.status_code} {response.text}")
                return []
        except Exception as e:
            print(f"Ошибка загрузки дат через GET-запрос: {e}")
            return []

    def get_schedule_data(self):
        try:
            response = requests.get("https://omuremes.pythonanywhere.com/schedules")
            if response.status_code == 200:
                schedules = response.json()
                filtered = [entry for entry in schedules if entry['title'] == self.title]
                halls = list({entry['hall'] for entry in filtered})
                times = list({entry['time'] for entry in filtered})
                prices = list({f"{entry['price']} сом" for entry in filtered})
                return sorted(halls), sorted(times, key=lambda x: tuple(map(int, x.replace(":", " ").split()))), sorted(prices)
            else:
                print(f"Ошибка запроса: {response.status_code} {response.text}")
                return [], [], []
        except Exception as e:
            print(f"Ошибка загрузки расписания через GET-запрос: {e}")
            return [], [], []
    def get_selected_date(self):
        for i in range(self.date_layout.count()):
            button = self.date_layout.itemAt(i).widget()
            if button:
                print(f"Кнопка: {button.text()}, Состояние: {button.isChecked()}")  # Отладочный вывод
                if button.isChecked():
                    return button.text()
        return None
 # Если дата не выбрана
 # Если дата не выбрана

    def open_seat_selection(self, hall, date, time, price):
        selected_date = self.get_selected_date()  # Получаем выбранную дату
        if not selected_date:  # Если дата не выбрана
            QMessageBox.warning(self, "Ошибка", "Выберите дату.")
            return

        # Создаём окно выбора мест
        self.seats_window = SeatSelection(
            username=self.username,
            movie_title=self.title,
            hall=hall,
            date=selected_date,  # Передаём выбранную дату
            time=time
        )
        self.seats_window.show()
        self.close()


   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieSchedule("images/image.jpg", "Интерстеллар")
    window.show()
    sys.exit(app.exec_())
