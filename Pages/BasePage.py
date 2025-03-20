from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    """Base page for pages to automate. Provides simple and common functions"""
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def run_driver(self):
        self.dr.get(self.url)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator):
        try: 
            btn = self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print("Timeout")
            self.quit()
        btn.click()
    
    def send_keys(self, locator, text):
        try: 
            field = self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print("Timeout")
            self.quit()
        field.send_keys(text)