from PySide6.QtWidgets import QApplication
from widgets.bootstrapwidget import BootstrapWidget

def main():    

    app = QApplication([])

    window = BootstrapWidget()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()