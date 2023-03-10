from PySide6.QtWidgets import QApplication
from widgets.downloadwidget import DownloadWidget

def main():
    app = QApplication([])

    window = DownloadWidget()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()