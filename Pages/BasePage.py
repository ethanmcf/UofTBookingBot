from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import TimeoutException
import time

class BasePage:
    """Base page for pages to automate. Provides simple and common functions"""
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator, submit = False):
        try: 
            btn = self.wait.until(EC.element_to_be_clickable(locator))
            if submit:
                btn.submit()
            else:
                btn.click()

        except TimeoutException:
            print("Timeout")
            self.quit()
    
    
    def send_keys(self, locator, text): 
        try: 
            self.wait.until(EC.element_to_be_clickable(locator)).send_keys(text)
        except TimeoutException:
            print("Timeout")
            self.quit()
        