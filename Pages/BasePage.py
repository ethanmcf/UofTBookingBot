from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time

class BasePage:
    """Base page for pages to automate. Provides simple and common functions"""
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator, submit = False):
        btn = self.wait.until(EC.element_to_be_clickable(locator), f"Timed out waiting for the following element to be clickable: {locator}.")
        if submit:
            btn.submit()
        else:
            btn.click()
    
    def send_keys(self, locator, text): 
        self.wait.until(EC.element_to_be_clickable(locator), f"Timed out waiting for the following element to be clickable: {locator}.").send_keys(text)

    def find_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator), f"Timed out waiting for the following element to be visible:  {locator}.")
    
    def random_sleep(self, expected_wait, variance = 0.1):
        min_wait = max(0, expected_wait - variance)
        max_wait = max(min_wait, expected_wait + variance)
        wait_secs = random.uniform(min_wait, max_wait)
        time.sleep(wait_secs)
    
    def scroll_by(self, top = 0, left = 0):
        # Exact integer values or ranges can be passed in for scroll amounts
        if top is tuple:
            top = random.randint(top[0], top[1])
        if left is tuple:
            left = random.randint(left[0], left[1])

        self.dr.execute_script(
            f"""window.scrollBy({{ 
            top: {top},
            left: {left}, 
            behavior: 'smooth' 
            }});"""
        )