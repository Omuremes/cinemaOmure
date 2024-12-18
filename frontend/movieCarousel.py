from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QLabel

from movieShedule import MovieSchedule
import requests
import os

class MovieCarousel(QWidget):
    def __init__(self,user_id):
        super().__init__()
        self.user_id = user_id

        self.setWindowTitle("Сетка фильмов")
        self.setStyleSheet("background-color: white;")
        self.setGeometry(100, 100, 1200, 800)

        # Список фильмов (изображения + названия)
        self.movies = []  # Динамически загружаемый список фильмов
        self.load_movies()  # Загрузка фильмов из API

        # Параметры пагинации
        self.movies_per_page = 6  # Количество фильмов на странице
        self.current_page = 0

        # Основной макет
        self.main_layout = QVBoxLayout(self)
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(30, 20, 20, 20)
        self.grid_layout.setSpacing(20)

        # Кнопки для переключения страниц и номер страницы
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.setSpacing(20)
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Кнопка "Предыдущая" с изображением
        self.prev_button = QPushButton()
        self.prev_button.setIcon(QIcon("images/arrow-left.png"))
        self.prev_button.setIconSize(QSize(40, 40))
        self.prev_button.setFixedSize(60, 60)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #dddddd;
                border-radius: 30px;
            }
        """)
        self.prev_button.clicked.connect(self.show_previous_page)

        # Кнопка "Следующая" с изображением
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon("images/arrow-right.png"))
        self.next_button.setIconSize(QSize(40, 40))
        self.next_button.setFixedSize(60, 60)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #dddddd;
                border-radius: 30px;
            }
        """)
        self.next_button.clicked.connect(self.show_next_page)

        # Номер текущей страницы
        self.page_label = QLabel("Страница: 1 / 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("font-size: 16px; color: black;")

        self.pagination_layout.addItem(spacer_left)
        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.next_button)
        self.pagination_layout.addItem(spacer_right)

        # Добавляем сетку и кнопки в основной макет
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addLayout(self.pagination_layout)

        # Отображаем фильмы
        self.update_grid()
    # Добавляем кнопку "Добавить" в левый нижний угол
        

    
    def load_movies(self):
        try:
            response = requests.get("https://omuremes.pythonanywhere.com/movies")
            if response.status_code == 200:
                self.movies = response.json()
                print("Загруженные фильмы:", self.movies)
            else:
                print("Ошибка загрузки фильмов")
        except Exception as e:
            print(f"Ошибка подключения: {e}")


    

    def open_booking_window(self, image_path, title):
        self.booking_window = MovieSchedule(username=self.user_id,image_path=image_path, title=title)

        self.booking_window.show()

    def update_grid(self):
        # Очищаем текущую сетку
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Вычисляем фильмы для текущей страницы
        start_index = self.current_page * self.movies_per_page
        end_index = start_index + self.movies_per_page
        movies_to_display = self.movies[start_index:end_index]

        cols = 3  # Количество фильмов в строке
        for i, movie in enumerate(movies_to_display):
            row = i // cols
            col = i % cols

            # Контейнер для фильма (изображение + заголовок)
            movie_layout = QVBoxLayout()
            movie_layout.setSpacing(0)  # Убираем отступы внутри контейнера

            # Изображение фильма
            image_label = QLabel()
            pixmap = QPixmap(movie["image_path"]).scaled(300, 2500, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
            image_label.setScaledContents(True)
            image_label.setFixedSize(300, 250)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("border: 2px solid #cccccc; border-radius: 10px;")
            image_label.mousePressEvent = lambda event, m=movie: self.open_schedule(m["title"])
            # Добавляем обработчик клика
            image_label.mousePressEvent = lambda event, m=movie: self.open_booking_window(
                m["image_path"], m["title"]
            )

            # Контейнер для заголовка
            title_container = QLabel(movie["title"])
            title_container.setFixedSize(300, 50)
            title_container.setStyleSheet("""
                background-color: #1E1E1E; 
                border: 2px solid #cccccc; 
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            """)
            title_container.setAlignment(Qt.AlignCenter)

            # Добавляем изображение и заголовок в контейнер
            movie_layout.addWidget(image_label)
            movie_layout.addWidget(title_container)

            # Оборачиваем контейнер в виджет и добавляем в сетку
            container = QWidget()
            container.setLayout(movie_layout)
            container.setFixedWidth(320)
            self.grid_layout.addWidget(container, row, col)

        # Обновляем состояние кнопок и номер страницы
        self.update_pagination_buttons()

    def update_pagination_buttons(self):
        total_pages = (len(self.movies) + self.movies_per_page - 1) // self.movies_per_page
        self.page_label.setText(f"Страница: {self.current_page + 1} / {total_pages}")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled((self.current_page + 1) * self.movies_per_page < len(self.movies))

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_grid()

    def show_next_page(self):
        if (self.current_page + 1) * self.movies_per_page < len(self.movies):
            self.current_page += 1
            self.update_grid()
    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MovieCarousel()
    window.show()
    sys.exit(app.exec())
