from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    