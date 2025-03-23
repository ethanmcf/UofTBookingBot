from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Pages.BasePage import BasePage

class LoginPage(BasePage):
    def __init__(self, driver, login_manager):
        super().__init__(driver)
        self.login_manager = login_manager
        self.utorid_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_btn = (By.ID, "login-btn")
        
    def login(self):
        username, password = self.login_manager.get_credentials()
        self.click(self.utorid_input)
        self.send_keys(self.utorid_input, username)
        self.click(self.password_input)
        self.send_keys(self.password_input, password)
        self.click(self.login_btn)
