from Pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import time

class SelectPage(BasePage):
    def __init__(self, driver, timing, wanted_date):
        super().__init__(driver)
        self.time_slot_card = (By.XPATH, f"//div[@class='card mb-4 d-flex' and @data-instance-dates='{wanted_date}' and @data-instance-times='{timing}']")
        self.select_btn = (By.XPATH, "//button[contains(@class, 'program-select-btn') and contains(text(), 'Select')]")
        self.registration_btn = (By.ID, 'registerBtn')

    def wait_for_time_slot(self):
        # Set the timeout duration to 5 minutes
        timeout = timedelta(seconds=2)
        end_time = datetime.now() + timeout
        card = None
        while datetime.now() < end_time:
            try:
                # Refresh the page
                self.dr.refresh()
                
                card = self.dr.find_element(self.time_slot_card)
                by, info = self.select_btn
                btn = card.find_element(by, info)
                btn.click()
                return True  
                
            except Exception as e:
                pass # no element found this iterations
    
        return False  # Return False if the timeout is reached
    
    def select(self):
        if not self.wait_for_time_slot():
            print("Timeout - no slot was found")
            self.quit()
            return

        # Handle possible cookie message
        cookie_message = self.dr.find_element(By.ID, "gdpr-cookie-message")
        cookie_close_btn = cookie_message.find_element(By.XPATH, ".//button")
        cookie_close_btn.click()

        # click registration
        self.click(self.registration_btn)