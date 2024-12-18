import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow  # Импортируем MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()  # Создаём объект MainWindow
    window.show()
    sys.exit(app.exec_())
