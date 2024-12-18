from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,QMessageBox
from PyQt5.QtGui import QFont,QCursor
from PyQt5.QtCore import Qt
from register_window import RegisterWindow  # Импортируем RegisterWindow
import requests
from movieCarousel import MovieCarousel
from adminPanel import AdminPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Авторизация")
        self.setFixedSize(600, 400)

        self.registerWindow = None  # Для хранения окна регистрации

        self.initUI()

    def initUI(self):
        self.backGround = QWidget(self)
        self.backGround.setGeometry(50, 50, 500, 300)
        self.backGround.setStyleSheet("background-color: #1E1E1E; border-radius: 50px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 10, 50, 10)
        layout.setSpacing(1)
        self.backGround.setLayout(layout)

        self.lineEditLogin = QLineEdit()
        self.lineEditLogin.setPlaceholderText("Введите имя")
        self.lineEditLogin.setFont(QFont("Arial", 12))
        self.lineEditLogin.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 10px;
            padding-left: 35px;
            height: 50px;
        """)
        layout.addWidget(self.lineEditLogin)

        self.lineEditPassword = QLineEdit()
        self.lineEditPassword.setPlaceholderText("Введите пароль")
        self.lineEditPassword.setFont(QFont("Arial", 12))
        self.lineEditPassword.setEchoMode(QLineEdit.Password)
        self.lineEditPassword.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 10px;
            padding-left: 35px;
            height: 50px;
        """)
        layout.addWidget(self.lineEditPassword)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.loginButton = QPushButton("Войти")
        self.loginButton.setFont(QFont("Arial", 10))
        self.loginButton.setFixedSize(100, 40)
        self.loginButton.setStyleSheet("""
        QPushButton {
            background-color: #FFFFFF;
            border-radius: 10px;
            transition: background-color 0.3s;
        }
        QPushButton:hover {
            background-color: #FFD700;
        }
        """)
        button_layout.addWidget(self.loginButton)
        self.loginButton.clicked.connect(self.handle_login)
        self.loginButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.registerButton = QPushButton("Регистрация")
        self.registerButton.setFont(QFont("Arial", 10))
        self.registerButton.setFixedSize(150, 40)
        self.registerButton.setStyleSheet("""
        QPushButton {
            background-color: #FFFFFF;
            border-radius: 10px;
            transition: background-color 0.5s;
        }
        QPushButton:hover {
            background-color: #FFD700;
        }
        """)
        self.registerButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.registerButton.clicked.connect(self.openRegisterWindow)  # Подключаем функцию
        button_layout.addWidget(self.registerButton)

        layout.addLayout(button_layout)

    def openRegisterWindow(self):
        self.hide()  # Скрываем главное окно
        if self.registerWindow is None:
            self.registerWindow = RegisterWindow(self)  # Создаём окно регистрации
        self.registerWindow.show()  # Показываем окно регистрации
    def handle_login(self):
        username = self.lineEditLogin.text()
        password = self.lineEditPassword.text()

        try:
            response = requests.post('https://omuremes.pythonanywhere.com/login', json={
                'username': username,
                'password': password
            })

            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Вход выполнен.")
                if username == "admin":
                    self.adminWindow = AdminPanel(username=username)  # Открываем окно для администратора
                    self.adminWindow.show()
                else:
                    self.movieCarouselWindow = MovieCarousel(user_id=username)  # Открываем окно для обычного пользователя
                    self.movieCarouselWindow.show()
                self.close()
                user_id = response.json().get("user_id")
                # Открываем окно MovieCarousel
            else:
                error_message = response.json().get('message', 'Ошибка при входе.')
                QMessageBox.warning(self, "Ошибка", error_message)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к серверу: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
