from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Pages.BasePage import BasePage

class DuoPage(BasePage):
    def __init__(self, driver, login_manager, has_trust_prompt = True):
        super().__init__(driver)
        self.login_manager = login_manager
        self.has_trust_prompt = has_trust_prompt
        self.other_options_btn = (By.XPATH, "//a[contains(text(), 'Other options')]")
        self.bypass_code_option_btn = (By.XPATH, "//a[.//div[contains(text(), 'Bypass code')]]")
        self.code_input = (By.ID, "passcode-input")
        self.code_submit_btn = (By.CLASS_NAME, "verify-button")
        self.trust_device_btn = (By.ID, "trust-browser-button")

    def bypass(self):
        print("Duo Page ... bypassing")
        self.click(self.other_options_btn)
        self.click(self.bypass_code_option_btn)
        self.click(self.code_input)

        code = self.login_manager.get_code()
        self.send_keys(self.code_input, code)
        self.click(self.code_submit_btn)

        if self.has_trust_prompt:
            self.click(self.trust_device_btn)
