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
from PySide6.QtCore import QStandardPaths, QDir, Slot
from PySide6.QtNetwork import QNetworkAccessManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict
from widgets.downloaderthread import DownloaderThread


class DownloadWidget(QWidget):

    def __init__(self, driver: webdriver.Chrome, parent=None):
        super().__init__(parent)

        self.setWindowTitle("RevaturePro Cohort Recording Scraper")

        self.driver = driver
        self.curriculum_url = self.driver.current_url

        # Setup Instructions Box
        self.instructions_container = QVBoxLayout()
        self.instructions_label = QLabel(
            """Instructions:
            1. In the browser, select the week to scrape (this must be done individually)
            2. Select your download location below
            3. Check each day in the current week you would like to scrape recordings from
            4. Click start!""")
        self.instructions_container.addWidget(self.instructions_label)

        # Setup download location Box
        self.dl_location_box = QLineEdit()
        self._select_dl_location_action = self.dl_location_box.addAction(
                QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), QLineEdit.ActionPosition.TrailingPosition
        )
        self._select_dl_location_action.triggered.connect(self.on_select_location)
        
        self.dl_location_box.setText(
            QDir.fromNativeSeparators(
                QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
            )
        )

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
        self.day_selector_group.buttonClicked.connect(self.on_select_day)
        for i in range(len(self.day_checkboxes)):
            self.day_selector_group.addButton(self.day_checkboxes[i], i)
            self.day_selector_container.addWidget(self.day_checkboxes[i])

        # Setup progress bar
        self.downloaded = 0
        self.to_download = 0
        self.progress_container = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Download Progress:")
        self.progress_label.setBuddy(self.progress_bar)
        self.downloaded_label = QLabel("0")
        self.separator_label = QLabel("/")
        self.to_download_label = QLabel("0")
        self.progress_container.addWidget(self.progress_label)
        self.progress_container.addWidget(self.progress_bar)
        self.progress_container.addWidget(self.downloaded_label)
        self.progress_container.addWidget(self.separator_label)
        self.progress_container.addWidget(self.to_download_label)

        # Setup file tree preview
        self.file_tree_container = QVBoxLayout()
        self.file_tree = QTreeWidget()
        self.file_tree.setColumnCount(2)
        self.file_tree.setHeaderLabels(["Recording", "URL"])
        self.file_tree_container.addWidget(self.file_tree)

        # Setup network handlers
        self.manager = QNetworkAccessManager(self)
        self.threads: Dict[str, DownloaderThread] = {}

        # Setup button bar
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.new_week_button = QPushButton("New Week")
        self.new_week_button.clicked.connect(self.return_to_curriculum)
        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch()
        self.button_bar.addWidget(self.start_button)
        self.button_bar.addWidget(self.cancel_button)
        self.button_bar.addWidget(self.new_week_button)
        
        # Setup main layout
        self.main_container = QVBoxLayout(self)
        self.main_container.addLayout(self.instructions_container)
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
        """ Invoked when the user opens the Select Download Location dialog """

        dir_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if dir_path:
            dest_dir = QDir(dir_path)
            self.dl_location_box.setText(QDir.fromNativeSeparators(dest_dir.path()))

    ###########################################################################

    @Slot()
    def on_select_day(self, button):
        """ Invoked whenever a user toggles a checkbox """
        button_id = self.day_selector_group.id(button)

        # make sure the user is actually on a valid page, else disallow updates
        if not "Week%20" in self.driver.current_url:
            for checkbox in self.day_selector_group.buttons():
                checkbox.setChecked(False)
            return
    
        # extract the week name from the URL, reset the file tree if needed
        week_str = "Week " + self.driver.current_url[-2:]
        week_item = None
        if not self.file_tree.topLevelItem(0):
            week_item = QTreeWidgetItem([week_str], 0)
            self.file_tree.addTopLevelItem(week_item)
        if not self.file_tree.topLevelItem(0).text(0) == week_str:
            self.file_tree.clear()
            week_item = QTreeWidgetItem([week_str], 0)
            self.file_tree.addTopLevelItem(week_item)
        else:
            week_item = self.file_tree.topLevelItem(0)

        # If the current day is unchecked, remove the day from the file tree
        if not self.day_selector_group.button(button_id).isChecked():
            days = self.file_tree.topLevelItem(0).childCount()
            for i in range(days):
                day = self.file_tree.topLevelItem(0).child(i)
                if day.text(0) == self.day_selector_group.button(button_id).text():
                    self.to_download -= day.childCount()
                    self.to_download_label.setNum(self.to_download)
                    self.file_tree.topLevelItem(0).removeChild(day)
                    break
            self.repaint()
            return
        
        # reset the downloaded count
        self.downloaded = 0
        self.downloaded_label.setNum(self.downloaded)
        
        day_element_list = self.driver.find_elements(By.CSS_SELECTOR, "#activitySideNav > div > div.panel-body.list-group > ul > div > div > h4")

        # if day selector is expanded, collapse it again
        for day in day_element_list:
            if day.find_element(By.XPATH, "..").get_attribute("aria-expanded") == "true":
                day.click()
        day_element = day_element_list[button_id]

        # create a day item for the tree, will hold recordings as children
        day_tree_item = QTreeWidgetItem([self.day_selector_group.button(button_id).text()], 0)

        # click the day in RevPro. Wait until the recordings dropdown loads 
        day_element.click()
        WebDriverWait(self.driver,5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#s2id_recordings-drop-down")))  
        # click the dropdown list. This reveals a <ul> we can click through
        self.driver.find_element(By.CSS_SELECTOR, "#s2id_recordings-drop-down").click()
        # get rid of a mask that intercepts further clicks
        self.driver.execute_script(""" mask=document.getElementById("select2-drop-mask"); if (mask) mask.remove() """)
        # capture the number of elements now, as they'll all get destroyed and recreated every time the dropdown list is refreshed
        count = len(self.driver.find_elements(By.CSS_SELECTOR, ".select2-results > li"))
        # close the dropdown so it can be reopened for each iteration
        self.driver.find_element(By.CSS_SELECTOR, "#s2id_recordings-drop-down").click()
        for j in range(count):
            # ensure the dropdown is expanded, make sure list elements are visible
            WebDriverWait(self.driver,2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#s2id_recordings-drop-down")))
            self.driver.find_element(By.CSS_SELECTOR, "#s2id_recordings-drop-down").click()
            # get rid of that mask that intercepts further clicks
            self.driver.execute_script(""" mask=document.getElementById("select2-drop-mask"); if (mask) mask.remove() """)
            # grab the <li> elements, extract the name of the current recording, and then click it to load the recording video
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ul[id^=\"select2-results\"] > li")))
            recording_list = self.driver.find_elements(By.CSS_SELECTOR, "ul[id^=\"select2-results\"] > li")
            recording_item_str = recording_list[j].find_element(By.CSS_SELECTOR, ".select2-result-label").text
            recording_list[j].click()
            # wait for the video player to load, then extract the URL. Add the recording item to the file tree
            WebDriverWait(self.driver,60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#recordingPlayer_html5_api")))
            recording_url = self.driver.find_element(By.CSS_SELECTOR, "#recordingPlayer_html5_api > source").get_attribute("ng-src")
            recording_tree_item = QTreeWidgetItem(str(j) + "_" + [recording_item_str.replace(':', '-').replace('/', '-').replace(' ', '_') + ".mp4", recording_url], 0)
            day_tree_item.addChild(recording_tree_item)
        self.to_download += day_tree_item.childCount()
        self.to_download_label.setNum(self.to_download)
        week_item.addChild(day_tree_item)
        
        self.file_tree.expandAll()

    ###########################################################################

    @Slot()
    def on_cancel(self):
        """ delete last reply and close file buffer """
        self.downloaded = 0
        self.downloaded_label.setNum(self.downloaded)
        self.progress_bar.setRange(0,1)
        
        for k, t in self.threads.items():
            t.terminate()

        self.threads = {}

        self.start_button.setDisabled(False)
        self.cancel_button.setDisabled(True)
        self.new_week_button.setDisabled(False)
    ###########################################################################

    @Slot()
    def return_to_curriculum(self):
        """ Redirects browser to curriculum URL """
        for checkbox in self.day_selector_group.buttons():
            checkbox.setChecked(False)
        self.downloaded = 0
        self.downloaded_label.setNum(self.downloaded)
        self.to_download = 0
        self.to_download_label.setNum(self.to_download)
        self.progress_bar.setRange(0,1)
        self.file_tree.clear()
        self.threads = {}
        self.driver.get(self.curriculum_url)
    ###########################################################################

    @Slot()
    def on_start(self):
        """ invoked when the user clicks the start button """

        self.start_button.setDisabled(True)
        self.cancel_button.setDisabled(False)
        self.new_week_button.setDisabled(True)
        self.progress_bar.setRange(0,1)

        # check if Week folder exists in DL location, and if not, create it
        week_dir = QDir(QDir.fromNativeSeparators(self.dl_location_box.text().strip() + "/" + self.file_tree.topLevelItem(0).text(0)))
        if not week_dir.exists():
            week_dir.mkpath(".")

        # iterate over selected days, create day folder if needed
        days = self.file_tree.topLevelItem(0).childCount()
        for i in range(days):
            day = self.file_tree.topLevelItem(0).child(i)
            day_dir = QDir(QDir.fromNativeSeparators(week_dir.absolutePath() + "/" + day.text(0)))
            if not day_dir.exists():
                day_dir.mkpath(".")
            recordings = day.childCount()
            # iterate over all recordings for a day, and download them
            for j in range(recordings):
                recording = day.child(j)
                dest_filename = recording.text(0)
                dest_url = recording.text(1)
                dest_file = day_dir.filePath(dest_filename)
                
                self.threads[dest_filename] = DownloaderThread(dest_url, dest_file, dest_filename)
                self.threads[dest_filename].add_total_progress.connect(self.update_progress_max)
                self.threads[dest_filename].add_current_progress.connect(self.update_progress)
                self.threads[dest_filename].thread_complete.connect(self.on_finish_dl)
                self.threads[dest_filename].start()
    ###########################################################################

    @Slot(int)
    def update_progress_max(self, filesize: int):
        current_max = self.progress_bar.maximum()
        self.progress_bar.setMaximum(current_max + filesize)
    ###########################################################################

    @Slot(int)
    def update_progress(self, new_bytes: int):
        current_val = self.progress_bar.value()
        self.progress_bar.setValue(current_val + new_bytes)
    ###########################################################################

    @Slot(str)
    def on_finish_dl(self, dest_filename):
        """ delete last reply and close file buffer """
        self.downloaded += 1
        self.downloaded_label.setNum(self.downloaded)

        self.threads.pop(dest_filename).deleteLater()

        if self.downloaded == self.to_download:
            self.start_button.setDisabled(False)
            self.cancel_button.setDisabled(True)
            self.new_week_button.setDisabled(False)
            self.progress_bar.setValue(self.progress_bar.maximum())
    ###########################################################################

    