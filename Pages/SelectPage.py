from Pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
import time

class SelectPage(BasePage):
    def __init__(self, driver, date, start_time, posting_offset, time_limit):
        super().__init__(driver)
        self.date = date
        self.start_time = start_time
        self.posting_offset = posting_offset
        self.time_limit = time_limit
        self.select_btn = (By.XPATH, "//button[contains(@class, 'program-select-btn') and contains(text(), 'Select')]")
        self.registration_btn = (By.ID, 'registerBtn')

        # Create a concrete locator for time slot card
        self.formatted_date = datetime.fromisoformat(self.date).strftime("%A, %B %d, %Y")
        self.formatted_start_time = datetime.strptime(self.start_time, "%H:%M").strftime("%-I:%M %p")
        self.time_slot_card = (By.XPATH, f"//div[@class='card mb-4 d-flex' and @data-instance-dates='{self.formatted_date}' and starts-with(@data-instance-times, '{self.formatted_start_time}')]")

    def wait_for_url_to_start(self):
        WebDriverWait(self.dr, 60).until(
            lambda driver: driver.current_url.startswith("https://recreation.utoronto.ca/")
        )

    def wait_for_time_slot(self):
        # Wait for url
        self.wait_for_url_to_start()

        # Wait until registration opens if nec.
        if self.posting_offset:
            activity_datetime = datetime.strptime(f"{self.date} {self.start_time}:00", "%Y-%m-%d %H:%M:%S")
            wakeup_datetime = activity_datetime - timedelta(days=self.posting_offset) - timedelta(seconds=3)
            diff_time = wakeup_datetime - datetime.now()
            sleep_seconds = max(0, diff_time.total_seconds())

            print(f"Waiting for {sleep_seconds} second(s)", end="")
            if sleep_seconds > 0:
                print(f" until {wakeup_datetime.strftime("%A, %B %d, %Y at %-I:%M:%S %p")}", end="")
            print("...")

            time.sleep(sleep_seconds)

        print(f"Registering for drop-in activity on {self.formatted_date} at {self.formatted_start_time}...")

        # Continually wait for the registration button to appear (capped by a time limit)
        stopping_datetime = datetime.now() + timedelta(seconds=self.time_limit)
        while True:
            try:
                # Refresh the page
                self.dr.refresh()

                # Look for the correct time slot to press
                card = self.dr.find_element(*self.time_slot_card)
                btn = card.find_element(*self.select_btn)
                btn.click()

                break
            except Exception:
                # No element found this iteration -> throttle refresh rate slightly (~100ms)
                time.sleep(0.1)

                # Stop checking once we reach our maximum time limit
                if datetime.now() >= stopping_datetime:
                    return False
        
        return True
            
    
    def select(self):
        if not self.wait_for_time_slot():
            raise Exception("Timeout - registration slot could not be found within 10 seconds.")

        # Handle possible cookie message
        try:
            cookie_message = self.dr.find_element(By.ID, "gdpr-cookie-message")
            cookie_close_btn = cookie_message.find_element(By.XPATH, ".//button")
            cookie_close_btn.click()
        except NoSuchElementException:
            pass

        # Click registration
        self.click(self.registration_btn)
        