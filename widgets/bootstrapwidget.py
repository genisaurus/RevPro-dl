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
import time


class BootstrapWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("RevaturePro Cohort Recording Scraper")

        # Setup Instructions Box
        self.instructions_container = QVBoxLayout()
        self.instructions_label = QLabel("Instructions:\nStep 1: Log into RevaturePro using the opened Chrome window, then click \"Next\"")
        self.instructions_container.addWidget(self.instructions_label)

        # Setup button bar
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(True)
        self.next_button.clicked.connect(self.next_instruction)
        self.button_bar = QHBoxLayout()
        self.button_bar.addStretch()
        self.button_bar.addWidget(self.next_button)

        # Setup main layout
        self.main_container = QVBoxLayout(self)
        self.main_container.addLayout(self.instructions_container)
        self.main_container.addLayout(self.button_bar)
        self.main_container.addStretch()
        self.resize(401,105)

        # Wait for login, then activate button
        self.driver = webdriver.Chrome()
        self.driver.get("http://app.revature.com/")

    @Slot()
    def next_instruction(self):
        self.next_button.setEnabled(False)
        self.instructions_label.setText("Instructions:\nStep 2: Select the curriculum you wish to scrape from")
        self.repaint()
        WebDriverWait(self.driver, 600).until(EC.title_contains("Dashboard"))
        self.driver.get("http://app.revature.com/curricula")
        wait = WebDriverWait(self.driver, 600).until(EC.url_contains("curriculum"))
        WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "button.fc-detailedView-button"))
        detailed_view_button = self.driver.find_element(By.CSS_SELECTOR, "button.fc-detailedView-button")
        detailed_view_button.click()
        self.scraper_window = DownloadWidget(self.driver)
        self.scraper_window.show()
        self.hide()