from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QMessageBox,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QStyle,
    QFileDialog,
)
from PySide6.QtCore import QStandardPaths, QUrl, QFile, QSaveFile, QDir, QIODevice, Slot
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from PySide6.QtGui import QIcon, QPixmap
import sys
import os

class DownloadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("RevaturePro Cohort Recording Scraper")

        print(os.path.abspath("icons/folder-horizontal-open.png"))
        print(os.path.exists("icons/folder-horizontal-open.png"))

        # Setup download location Box
        self.dl_location_box = QLineEdit()
        self._select_dl_location_action = self.dl_location_box.addAction(
                QIcon("icons/folder-horizontal-open.png"), QLineEdit.ActionPosition.TrailingPosition
        )
        self._select_dl_location_action.triggered.connect(self.on_select_location)
        
        self.dl_location_box.setText(
            QDir.fromNativeSeparators(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
            )
        )

        # Setup progress bar
        self.progress_bar = QProgressBar()

        # Setup Network/File handlers
        self.manager = QNetworkAccessManager(self)
        self.current_file = None
        self.last_reply = None

        # Setup button bar
        self.start_button = QPushButton("Start")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        button_bar = QHBoxLayout()
        button_bar.addStretch()
        button_bar.addWidget(self.start_button)
        button_bar.addWidget(self.cancel_button)
        
        # Setup main layout
        container = QVBoxLayout(self)
        container.addWidget(self.dl_location_box)
        container.addWidget(self.progress_bar)
        container.addStretch()
        container.addLayout(button_bar)

        self.resize(640, 480)
    
    @Slot()
    def on_select_location(self):

        dir_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if dir_path:
            dest_dir = QDir(dir_path)
            self.dl_location_box.setText(QDir.fromNativeSeparators(dest_dir.path()))