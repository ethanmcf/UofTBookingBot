from Pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import time

class SelectPage(BasePage):
    def __init__(self, driver, hour, times, wanted_date):
        super().__init__(driver)
        self.time_slot_card = (By.XPATH, f"//div[@class='card mb-4 d-flex' and @data-instance-dates='{wanted_date}' and @data-instance-times='{times}']")
        self.select_btn = (By.XPATH, "//button[contains(@class, 'program-select-btn') and contains(text(), 'Select')]")
        self.registration_btn = (By.ID, 'registerBtn')
        self.date = wanted_date
        self.hour = hour

    def wait_for_url_to_start(self):
        try:
            WebDriverWait(self.dr, 60).until(
                lambda driver: driver.current_url.startswith("https://recreation.utoronto.ca/")
            )
        except:
            print("Took too long to login")
            self.quit()

    def wait_for_time_slot(self):
        # Wait for url
        self.wait_for_url_to_start()

        target_datetime = datetime.strptime(f"{self.date} {self.hour}", "%A, %B %d, %Y %H:%M:%S")
        current_datetime = datetime.now() + timedelta(days=2) 
        dif_time = target_datetime - current_datetime - timedelta(seconds=10) 
        sleep_seconds = dif_time.total_seconds() 
        print("Waiting for", sleep_seconds if sleep_seconds > 0 else 0, "seconds...")
        time.sleep(sleep_seconds if sleep_seconds > 0 else 0)
        print("Registering for drop-in activity...")

        card = None
        while True:
            try:
                # only refresh page if on the correct url page (elminates refreshing when loging in)
                if self.dr.current_url.startswith("https://recreation.utoronto.ca/"):
                    # Refresh the page
                    self.dr.refresh()
                    
                    card = self.dr.find_element(self.time_slot_card)
                    by, info = self.select_btn
                    btn = card.find_element(by, info)
                    btn.click()
                    return 
                
            except Exception as e:
                pass # no element found this iterations
    
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