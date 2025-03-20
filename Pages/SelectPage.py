from BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta

class SelectPage(BasePage):
    def __init__(self, driver, timing):
        super().__init__(driver)
        # exaclty two days from now 
        wanted_date = (datetime.now() + timedelta(days=2)).strftime("%A, %B %d, %Y")
        self.time_slot_card = (By.XPATH, f"//div[@class='card mb-4 d-flex' and @data-instance-dates='{wanted_date}' and @data-instance-times='{timing}']")
        self.select_btn = (By.XPATH, "//button[contains(@class, 'program-select-btn') and contains(text(), 'Select')]")
        self.registration_btn = (By.ID, 'registerBtn')

    
    def select(self):
        card = None
        try: 
            card = self.wait.until(EC.visibility_of_element_located(self.time_slot_card))
        except TimeoutException:
            print("Timeout")
            self.quit()

        by, info = self.select_btn
        btn = card.find_element(by, info)
        btn.click()

        # Handle possible cookie message
        cookie_message = self.dr.find_element(By.ID, "gdpr-cookie-message")
        cookie_close_btn = cookie_message.find_element(By.XPATH, ".//button")
        cookie_close_btn.click()

        # click registration
        self.click(self.registration_btn)