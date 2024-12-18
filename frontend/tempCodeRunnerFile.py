from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QLabel
from changeMovie import ChangeMovieWindow
import sqlite3

def load_movies_from_db(self):
    """Загружает фильмы из базы данных."""
    self.movies = []  # Очищаем текущий список фильмов
    try:
        conn = sqlite3.connect('movies.db')  # Подключение к базе данных
        cursor = conn.cursor()
        # Выполняем запрос для получения фильмов
        cursor.execute("SELECT image_path, title FROM movies")
        for row in cursor.fetchall():
            self.movies.append({"image": row[0], "title": row[1]})
        conn.close()
    except Exception as e:
        print(f"Ошибка при загрузке фильмов: {e}")



class MovieGrid(QWidget):
    """Сетка фильмов с поддержкой пагинации и названиями под изображениями"""
    def __init__(self):
        super().__init__()

    
        self.setWindowTitle("Сетка фильмов")
        self.setStyleSheet("background-color: white;")
        self.setGeometry(100, 100, 1200, 800)

        # Список фильмов (изображения + названия)
        self.movies = [
            {"image": "images/movie1.jpg", "title": "Фильм 1"},
            {"image": "images/movie2.jpg", "title": "Фильм 2"},
            {"image": "images/movie3.jpg", "title": "Фильм 3"},
            {"image": "images/movie4.jpg", "title": "Фильм 4"},
            {"image": "images/movie5.jpg", "title": "Фильм 5"},
            {"image": "images/movie6.jpg", "title": "Фильм 6"},
            {"image": "images/movie7.jpg", "title": "Фильм 7"},
            {"image": "images/movie8.jpg", "title": "Фильм 8"},
            {"image": "images/movie9.jpg", "title": "Фильм 9"},
            {"image": "images/movie10.jpg", "title": "Фильм 10"},
        ]

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
        self.add_button = QPushButton("Добавить")
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

        # Размещаем кнопку "Добавить" в нижнем левом углу
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)
        self.main_layout.addLayout(button_layout)
    def open_change_movie_window(self):
        """Открывает окно для добавления новых фильмов"""
        self.change_window = ChangeMovieWindow()
        self.change_window.show()


    def update_grid(self):
        """Обновляет фильмы в сетке"""
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
            pixmap = QPixmap(movie["image"])
            image_label.setPixmap(pixmap)
            image_label.setScaledContents(True)  # Масштабирует изображение на весь QLabel
            image_label.setFixedSize(300, 250)  # Устанавливаем фиксированный размер контейнера
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("""
                border: 2px solid #cccccc; 
                border-radius: 10px;
            """)

            # Контейнер для заголовка
            title_container = QLabel()
            title_container.setFixedSize(300, 50)  # Задаём фиксированный размер для контейнера заголовка
            title_container.setStyleSheet("""
                background-color: #1E1E1E; 
                border: 2px solid #cccccc; 
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            """)
            title_container.setText(movie["title"])
            title_container.setAlignment(Qt.AlignCenter)

            # Добавляем изображение и заголовок в контейнер
            movie_layout.addWidget(image_label)
            movie_layout.addWidget(title_container)

            # Оборачиваем контейнер в виджет и добавляем в сетку
            container = QWidget()
            container.setLayout(movie_layout)
            container.setFixedWidth(320)  # Фиксируем ширину контейнера
            self.grid_layout.addWidget(container, row, col)

        # Обновляем состояние кнопок и номер страницы
        self.update_pagination_buttons()

    def update_pagination_buttons(self):
        """Обновляет состояние кнопок пагинации и номер страницы"""
        total_pages = (len(self.movies) + self.movies_per_page - 1) // self.movies_per_page
        self.page_label.setText(f"Страница: {self.current_page + 1} / {total_pages}")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled((self.current_page + 1) * self.movies_per_page < len(self.movies))

    def show_previous_page(self):
        """Отображает предыдущую страницу"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_grid()

    def show_next_page(self):
        """Отображает следующую страницу"""
        if (self.current_page + 1) * self.movies_per_page < len(self.movies):
            self.current_page += 1
            self.update_grid()


    
    
class MovieCarousel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Carousel")
        self.setGeometry(100, 100, 1200, 800)
        self.initUI()

    def initUI(self):
        # Основной виджет
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Основной макет
        layout = QVBoxLayout()
        self.centralWidget.setLayout(layout)

        # Добавляем MovieGrid
        self.movieGrid = MovieGrid()  # Экземпляр MovieGrid
        layout.addWidget(self.movieGrid)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MovieGrid()
    window.show()
    sys.exit(app.exec())
