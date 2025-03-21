from selenium.webdriver.common.by import By
from Pages.BasePage import BasePage
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
        self.send_keys(self.utorid_input, "")
        time.sleep(1)
        self.click(self.password_input)
        self.send_keys(self.password_input, "")
        time.sleep(1)
        self.click(self.login_btn)
