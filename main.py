import sys
from PyQt6.QtWidgets import QApplication
from todo_app import TodoApp

def main():
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 