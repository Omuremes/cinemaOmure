from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget,QMessageBox
from PyQt5.QtGui import QFont,QCursor
from PyQt5.QtCore import Qt
import requests


class RegisterWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window  # Сохраняем ссылку на главное окно

        self.setWindowTitle("Регистрация")
        self.setFixedSize(600, 400)  # Размер окна

        self.initUI()

    def initUI(self):
        # Основной фон (BackGround)
        self.backGround = QWidget(self)
        self.backGround.setGeometry(50, 50, 500, 300)  # Размер фона
        self.backGround.setStyleSheet("background-color: #1E1E1E; border-radius: 50px;")

        # Макет для BackGround
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)  # Отступы внутри фона
        layout.setSpacing(20)  # Расстояние между элементами
        self.backGround.setLayout(layout)

        # Поле для имени пользователя
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setPlaceholderText("Введите имя пользователя")
        self.nameLineEdit.setFont(QFont("Arial", 12))
        self.nameLineEdit.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 10px;
            height: 50px;
        """)
        layout.addWidget(self.nameLineEdit)

        # Поле для пароля
        self.repeatPasswordLineEdit = QLineEdit()
        self.repeatPasswordLineEdit.setPlaceholderText("Введите пароль")
        self.repeatPasswordLineEdit.setFont(QFont("Arial", 12))
        self.repeatPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.repeatPasswordLineEdit.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 10px;
            height: 50px;
        """)
        layout.addWidget(self.repeatPasswordLineEdit)

        # Поле для подтверждения пароля
        self.repeatPasswordLineEdit_2 = QLineEdit()
        self.repeatPasswordLineEdit_2.setPlaceholderText("Повторите пароль")
        self.repeatPasswordLineEdit_2.setFont(QFont("Arial", 12))
        self.repeatPasswordLineEdit_2.setEchoMode(QLineEdit.Password)
        self.repeatPasswordLineEdit_2.setStyleSheet("""
            background-color: #FFFFFF;
            border-radius: 15px;
            height: 50px;
        """)
        layout.addWidget(self.repeatPasswordLineEdit_2)

        # Горизонтальный блок для кнопок
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Расстояние между кнопками

        # Кнопка "Назад"
        self.backButton = QPushButton("Назад")
        self.backButton.setFont(QFont("Arial", 10))
        self.backButton.setFixedSize(120, 40)
        self.backButton.setStyleSheet("""
        QPushButton {
            background-color: #FFFFFF;
            border-radius: 10px;
            transition: background-color 0.3s;
        }
        QPushButton:hover {
            background-color: #FFD700;
        }
        """)
        self.backButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.backButton.clicked.connect(self.go_back)  # Обработчик кнопки "Назад"
        button_layout.addWidget(self.backButton)

        # Кнопка "Регистрация"
        self.registerButton = QPushButton("Регистрация")
        self.registerButton.setFont(QFont("Arial", 10))
        self.registerButton.setFixedSize(150, 40)
        self.registerButton.setStyleSheet("""
        QPushButton {
            background-color: #FFFFFF;
            border-radius: 15px;
            transition: background-color 0.3s;
        }
        QPushButton:hover {
            background-color: #FFD700;
        }
        """)
        self.registerButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.registerButton.clicked.connect(self.handle_register)  # Подключаем правильный обработчик
        button_layout.addWidget(self.registerButton)

        layout.addLayout(button_layout)

    def handle_register(self):
        username = self.nameLineEdit.text()
        password = self.repeatPasswordLineEdit.text()
        confirm_password = self.repeatPasswordLineEdit_2.text()
        
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return
        
        try:
            response = requests.post('https://omuremes.pythonanywhere.com/register', json={
                'username': username,
                'password': password
            })
            if response.status_code == 200:
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно.")
            else:
                error_message = response.json().get('message', 'Ошибка при регистрации.')
                QMessageBox.warning(self, "Ошибка", error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к серверу: {str(e)}")

    def go_back(self):
        self.close()  # Закрываем окно регистрации
        self.main_window.show()  # Показываем главное окно

    def show_message(self, title, message):
        from PyQt5.QtWidgets import QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if title == "Успех" else QMessageBox.Warning)
        msg_box.exec_()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = RegisterWindow(None)
    window.show()
    app.exec()
