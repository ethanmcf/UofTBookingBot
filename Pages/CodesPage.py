from Pages.BasePage import BasePage
from selenium.webdriver.common.by import By
import re

class CodesPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.get_codes_btn = (By.XPATH, "//button[@name='generate']")
        self.codes_div = (By.TAG_NAME, "main")

    
    def generate_codes(self):
        self.click(self.get_codes_btn, submit=True)
        content = self.dr.find_element(By.TAG_NAME, "main").text
        codes = re.findall(r"\d{9}", content)
        return codes
        
