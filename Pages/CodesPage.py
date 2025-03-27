from Pages.BasePage import BasePage
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

class CodesPage(BasePage):
    def __init__(self, driver, login_manager):
        super().__init__(driver)
        self.login_manager = login_manager
        self.get_codes_btn = (By.NAME, "generate")
        self.main = (By.TAG_NAME, "main")
        
    def generate_codes(self):
        print("Codes Page ... generating codes")
        # Generate codes
        self.click(self.get_codes_btn, submit=True, sleep_params=(1, 0.3)) 

        # Extract codes
        content = self.find_element(self.main).text
        codes = re.findall(r"\d{9}", content)
        if not codes:
            raise Exception("No codes found during bypass code extraction.")

        # Save codes locally
        self.login_manager.save_codes(codes)
        