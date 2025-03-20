from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BasePage:
    """Base page for pages to automate. Provides simple and common functions"""
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator):
        try: 
            btn = self.wait.until(EC.element_to_be_clickable(locator))
            btn.click()
        except TimeoutException:
            print("Timeout")
            self.quit()
        
    
    def send_keys(self, locator, text):
        try: 
            field = self.wait.until(EC.presence_of_element_located(locator))
            field.send_keys(text)
        except TimeoutException:
            print("Timeout")
            self.quit()
        