from PySide6.QtWidgets import (
    QApplication,
    QStyle,
    QWidget,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem
)
from PySide6.QtCore import QStandardPaths, QUrl, QFile, QSaveFile, QDir, QIODevice, Slot
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from PySide6.QtGui import QIcon
import sys
import os

class DownloadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("RevaturePro Cohort Recording Scraper")

        # Setup download location Box
        self.dl_location_box = QLineEdit()
        self._select_dl_location_action = self.dl_location_box.addAction(
                QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), QLineEdit.ActionPosition.TrailingPosition
        )
        self._select_dl_location_action.triggered.connect(self.on_select_location)
        
        #self.dl_location_box.setText(
        #    QDir.fromNativeSeparators(
        #        QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        #    )
        #)

        self.dl_container = QHBoxLayout()
        self.dl_location_label = QLabel("Download Location:")
        self.dl_location_label.setBuddy(self.dl_location_box)
        self.dl_container.addWidget(self.dl_location_label)
        self.dl_container.addWidget(self.dl_location_box)

        # Setup day selector
        self.day_selector_container = QHBoxLayout()
        self.day_selector_group = QButtonGroup()
        self.day_selector_group.setExclusive(False)
        self.day_checkboxes = [QCheckBox("Day 1"), QCheckBox("Day 2"), QCheckBox("Day 3"), QCheckBox("Day 4"), QCheckBox("Day 5")]
        for i in range(len(self.day_checkboxes)):
            self.day_checkboxes[i].clicked.connect(self.on_select_day)
            self.day_selector_group.addButton(self.day_checkboxes[i])
            self.day_selector_container.addWidget(self.day_checkboxes[i])

        # Setup progress bar
        self.progress_container = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Download Progress:")
        self.progress_label.setBuddy(self.progress_bar)
        self.progress_container.addWidget(self.progress_label)
        self.progress_container.addWidget(self.progress_bar)

        # Setup file tree preview
        self.file_tree_container = QVBoxLayout()
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("File Tree")
        self.file_tree_container.addWidget(self.file_tree)

        # Setup Network/File handlers
        self.manager = QNetworkAccessManager(self)
        self.current_file = None
        self.last_reply = None

        # Setup button bar
        self.start_button = QPushButton("Start")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch()
        self.button_bar.addWidget(self.start_button)
        self.button_bar.addWidget(self.cancel_button)
        
        # Setup main layout
        self.main_container = QVBoxLayout(self)
        self.main_container.addLayout(self.dl_container)
        self.main_container.addLayout(self.day_selector_container)
        self.main_container.addLayout(self.file_tree_container)
        self.main_container.addLayout(self.progress_container)
        self.main_container.addLayout(self.button_bar)
        self.main_container.addStretch()

        self.resize(401, 480)
    ###########################################################################

    @Slot()
    def on_select_location(self):

        dir_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if dir_path:
            dest_dir = QDir(dir_path)
            self.dl_location_box.setText(QDir.fromNativeSeparators(dest_dir.path()))
            for checkbox in self.day_selector_group.buttons():
                checkbox.setChecked(False)
            self.file_tree.clear()
            self.file_tree.addTopLevelItem(QTreeWidgetItem([dest_dir.dirName()], QTreeWidgetItem.ItemType.Type))


    @Slot()
    def on_select_day(self):
        print("placeholder - will update file tree")