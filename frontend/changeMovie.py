from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QDateEdit, QTimeEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import json
import os
import shutil,requests

class ChangeMovieWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить фильм")
        self.setFixedSize(800, 600)
        self.initUI()

    def initUI(self):
        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Поле для ввода названия фильма
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Название фильма")
        main_layout.addWidget(self.title_input)

        # Поле для выбора изображения
        image_layout = QHBoxLayout()
        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("Путь к изображению")
        image_layout.addWidget(self.image_input)

        select_image_button = QPushButton("Выбрать изображение")
        select_image_button.clicked.connect(self.select_image)
        image_layout.addWidget(select_image_button)
        main_layout.addLayout(image_layout)

        # Блок для добавления расписания
        self.schedule_layout = QVBoxLayout()

        add_schedule_button = QPushButton("Добавить расписание")
        add_schedule_button.clicked.connect(self.add_schedule_row)
        main_layout.addWidget(add_schedule_button)
        main_layout.addLayout(self.schedule_layout)

        # Кнопка для сохранения
        save_button = QPushButton("Сохранить фильм и расписание")
        save_button.clicked.connect(self.save_movie_and_schedule)
        main_layout.addWidget(save_button)

        self.setLayout(main_layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_input.setText(file_path)

    def add_schedule_row(self):
        row_layout = QHBoxLayout()

        date_input = QDateEdit()
        date_input.setCalendarPopup(True)
        row_layout.addWidget(date_input)

        time_input = QTimeEdit()
        row_layout.addWidget(time_input)

        hall_input = QLineEdit()
        hall_input.setPlaceholderText("Зал")
        row_layout.addWidget(hall_input)

        price_input = QSpinBox()
        price_input.setRange(0, 10000)
        row_layout.addWidget(price_input)

        remove_button = QPushButton("Удалить")
        remove_button.clicked.connect(lambda: self.remove_schedule_row(row_layout))
        row_layout.addWidget(remove_button)

        self.schedule_layout.addLayout(row_layout)

    def remove_schedule_row(self, row_layout):
        for i in reversed(range(row_layout.count())):
            widget = row_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.schedule_layout.removeItem(row_layout)

    def save_movie_and_schedule(self):
        title = self.title_input.text()
        image_path = self.image_input.text()

        if not title or not image_path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните название фильма и изображение.")
            return

        try:
            # Сохранение изображения в папку images
            dest_folder = "images"
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            dest_path = os.path.join(dest_folder, os.path.basename(image_path))
            shutil.copy(image_path, dest_path)

            # Отправка фильма на сервер
            new_movie = {"title": title, "image_path": dest_path}
            movie_response = requests.post("https://omuremes.pythonanywhere.com/movies", json=new_movie)

            if movie_response.status_code != 201:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить фильм: {movie_response.json().get('error', 'Неизвестная ошибка')}")
                return

            # Отправка расписания на сервер
            schedules = []
            for i in range(self.schedule_layout.count()):
                row_layout = self.schedule_layout.itemAt(i)
                date_input = row_layout.itemAt(0).widget().text()
                time_input = row_layout.itemAt(1).widget().text()
                hall_input = row_layout.itemAt(2).widget().text()
                price_input = row_layout.itemAt(3).widget().value()

                schedules.append({
                    "title": title,
                    "date": date_input,
                    "time": time_input,
                    "hall": hall_input,
                    "price": price_input
                })

            schedule_response = requests.post("https://omuremes.pythonanywhere.com/schedule", json=schedules)

            if schedule_response.status_code != 201:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить расписание: {schedule_response.json().get('error', 'Неизвестная ошибка')}")
                return

            QMessageBox.information(self, "Успех", "Фильм и расписание успешно сохранены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = ChangeMovieWindow()
    window.show()
    sys.exit(app.exec_())
