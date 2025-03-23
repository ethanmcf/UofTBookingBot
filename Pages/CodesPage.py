from Pages.BasePage import BasePage
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

class CodesPage(BasePage):
    def __init__(self, driver, login_manager):
        super().__init__(driver)
        self.login_manager = login_manager
        self.main = (By.TAG_NAME, "main")
        self.get_codes_btn = (By.NAME, "generate")
        self.codes_div = (By.XPATH, "/html/body/div/main/div")
        
    def generate_codes(self):
        # Generate codes
        main = self.find_element(self.main)
        self.click(self.get_codes_btn, submit=True)  # causes page to reload

        # Extract codes
        self.wait.until(EC.staleness_of(main))  # wait till page reloads
        content = self.find_element(self.codes_div).text
        codes = re.findall(r"\d{9}", content)

        # Save codes locally
        self.login_manager.save_codes(codes)
        