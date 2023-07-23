import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from screen import ScreenWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft Yahei", 9))

    ScreenWidget(None)

    sys.exit(app.exec())