from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from Pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
import time

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.utorid_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_btn = (By.ID, "login-btn")
        self.trust_device_btn = (By.ID, "")

    def login(self):
        self.click(self.utorid_input)
        self.send_keys(self.utorid_input, "mcfar135")
        time.sleep(1)
        self.click(self.password_input)
        self.send_keys(self.password_input, "Hellsatins7&")
        time.sleep(1)
        self.click(self.login_btn)
