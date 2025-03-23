from selenium.webdriver.common.by import By
from Pages.BasePage import BasePage
import time

class DuoPage(BasePage):
    def __init__(self, driver, login_manager):
        super().__init__(driver)
        self.login_manager = login_manager
        self.other_options_btn = (By.XPATH, "/html/body/div/div/div[1]/div/div[2]/div[6]/a")
        self.bypass_code_option_btn = (By.XPATH, "/html/body/div/div/div[1]/div/div[1]/ul/li[4]/a")
        self.code_input = (By.ID, "passcode-input")
        self.code_submit_btn = (By.XPATH, "/html/body/div/div/div[1]/div/div[2]/form/div[3]/button")
        self.trust_device_btn = (By.ID, "trust-browser-button")

    def bypass(self):
        code = self.login_manager.get_code()

        self.click(self.other_options_btn)
        self.click(self.bypass_code_option_btn)
        self.click(self.code_input)
        self.send_keys(self.code_input, code)
        self.click(self.code_submit_btn)
        self.click(self.trust_device_btn)
        time.sleep(5)
