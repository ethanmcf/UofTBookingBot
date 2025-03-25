import json
from Pages.BasePage import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.registration_btn = (By.ID, 'registerBtn')

        # Create a concrete locator for time slot button and select date button
        self.formatted_date = datetime.fromisoformat(self.date).strftime("%A, %B %d, %Y")
        self.formatted_start_datetime = datetime.strptime(f"{self.date} {self.start_time}:00", "%Y-%m-%d %H:%M:%S").strftime("%-m/%-d/%Y %-I:%M:%S %p")
        self.slot_btn = (By.XPATH, f"//button[@data-instance-starttime='{self.formatted_start_datetime}' and contains(@class, 'program-select-btn') and contains(text(), 'Select')]")
        self.select_date_btn = (By.XPATH, f"//button[contains(@class, 'date-selector-btn') and not(contains(@class, 'mobile')) and .//*[contains(text(), '{self.formatted_date}')]]")

    def short_wait_find_element(self, locator):
        return WebDriverWait(self.dr, 0.1).until(EC.element_to_be_clickable(locator))
    
    def wait_for_fetch_response(self, target_url, time_limit = 60):
        max_datetime = datetime.now() + timedelta(seconds=time_limit)
        while datetime.now() < max_datetime:
            logs = self.dr.get_log("performance")
            for log in logs:
                message = log["message"]       
                if "Network.responseReceived" not in message:
                    continue

                params = json.loads(message)["message"].get("params")
                if not params:
                    continue
                
                response = params.get("response")
                if response and response["url"].startswith(target_url):
                    return
                
            time.sleep(0.1)

    def wait_for_time_slot(self):
        # Wait until registration opens if nec.
        if self.posting_offset:
            activity_datetime = datetime.strptime(f"{self.date} {self.start_time}:00", "%Y-%m-%d %H:%M:%S")
            wakeup_datetime = activity_datetime - timedelta(days=self.posting_offset) - timedelta(seconds=3)
            diff_time = wakeup_datetime - datetime.now()
            sleep_seconds = max(0, diff_time.total_seconds())

            print(f"Waiting for {sleep_seconds} second(s)", end="")
            if sleep_seconds > 0:
                print(f" until {wakeup_datetime.strftime('%A, %B %d, %Y at %-I:%M:%S %p')}", end="")
            print("...")

            time.sleep(sleep_seconds)

        print(f"Registering for drop-in activity on {self.formatted_start_datetime}...")
        
        # Continually wait for the registration button to appear (capped by a time limit)
        self.dr.get_log("performance") # clear logs to start fresh
        stopping_datetime = datetime.now() + timedelta(seconds=self.time_limit)
        while True:
            try:
                # Ensure we are on the right page 
                if not self.dr.current_url.startswith("https://recreation.utoronto.ca/"):
                    raise Exception("Bot illegally navigated to a non drop-in website.")

                # Refresh the page
                self.dr.refresh()

                # Wait for date select button data to load
                self.wait_for_fetch_response("https://recreation.utoronto.ca/Program/GetProgramInstances")

                # Look for correct date and time selection
                select_date_btn = self.short_wait_find_element(self.select_date_btn)
                select_date_btn.click()

                # Wait for time slot data to load
                self.wait_for_fetch_response("https://recreation.utoronto.ca/Program/FilterProgramInstances")

                # Look for the correct time slot to press
                slot_btn =  self.short_wait_find_element(self.slot_btn)

                # Click the time slot if it is enabled
                if not slot_btn.is_enabled():
                    raise Exception("Desired time slot button is disabled.")
                slot_btn.click()

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
            raise Exception(f"Timeout - registration slot could not be found/accessed within {self.time_limit} seconds.")

        # Handle possible cookie message
        try:
            cookie_message = self.dr.find_element(By.ID, "gdpr-cookie-message")
            cookie_close_btn = cookie_message.find_element(By.XPATH, ".//button")
            cookie_close_btn.click()
        except NoSuchElementException:
            pass

        # Click registration
        self.click(self.registration_btn)
        