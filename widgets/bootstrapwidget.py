from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel
)
from PySide6.QtCore import Slot
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from widgets.downloadwidget import DownloadWidget


class BootstrapWidget(QWidget):

    def __init__(self, parent=None):

        self.setWindowTitle("RevaturePro Cohort Recording Scraper")

        # Setup Instructions Box
        self.instructions_container = QVBoxLayout()
        self.instructions_label = QLabel(
            """Instructions:
                Step 1: Log into RevaturePro using the opened Chrome window""")
                # 2. Select the curriculum you wish to scrape from
                # 3. Select the week to scrape (this must be done individually)
                # 4. In the GUI, select your download location
                # 5. Check each day in the current week you would like to scrape recordings from
                # 6. Click start!)
        self.instructions_container.addWidget(self.instructions_label)

        # Setup button bar
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_instruction)
        self.done_button = QPushButton("Done")
        self.done_button.setEnabled(False)
        self.done_button.clicked.connect(self.open_scraper)
        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch()
        self.button_bar.addWidget(self.next_button)
        self.button_bar.addWidget(self.done_button)

        # Setup main layout
        self.main_container = QVBoxLayout(self)
        self.main_container.addLayout(self.instructions_container)
        self.main_container.addStretch()
        self.main_container.addLayout(self.button_bar)
        self.resize(401,100)

        # Wait for login, then activate button
        self.driver = webdriver.Chrome()
        self.driver.get("http://app.revature.com/")

        WebDriverWait(self.driver, 600).until(EC.title_contains("Dashboard"))
        self.driver.get("http://app.revature.com/curricula")
        self.next_button.setEnabled(True)

    @Slot()
    def next_instruction(self):
        self.instructions_label.setText("""
            Instructions:
                Step 2: Select the curriculum you wish to scrape from""")
        wait = WebDriverWait(self.driver, 600).until(EC.url_contains("curriculum"))
        detailed_view_button = self.driver.find_element(By.CSS_SELECTOR, "#calendar > div.fc-toolbar.fc-header-toolbar > div.fc-right > div > button.fc-detailedView-button.fc-button.fc-button-primary")
        detailed_view_button.click()
        self.done_button.setEnabled(True)

    @Slot()
    def open_scraper(self):
        window = DownloadWidget()
        window.driver = self.driver
        window.show()
        self.close()