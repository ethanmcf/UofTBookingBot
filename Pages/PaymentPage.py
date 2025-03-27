from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Pages.BasePage import BasePage
import time

class PaymentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.next_btn = (By.CSS_SELECTOR, ".desktop .btn-NextRegistrationStep")
        self.expand_waiver_btn = (By.XPATH, "//button[@data-target='#regWaiver-collapse-1']")
        self.accept_btn = (By.CLASS_NAME, "btn-success.btnAccept")
        self.proceed_checkout_btn = (By.XPATH, "//div[contains(@class, 'stepActionButtons desktop')]//button[contains(@class, 'btn-NextRegistrationStep')]")

    def is_captcha_present(self):
        try:
            # Check for a common CAPTCHA element (update XPath based on the site)
            captcha_element = self.dr.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
            return len(captcha_element) > 0
        except Exception:
            return False
    
    def purchase(self):
        print("Payment Page ... purchasing")
        
        self.click(self.next_btn, sleep_params=(1, 0.3))

        self.click(self.expand_waiver_btn, sleep_params=(1, 0.3))

        self.click(self.accept_btn, sleep_params=(1, 0.3))

        self.random_sleep(3, variance=0.5)
        num_clicks = 0
        while(num_clicks < 20 and self.dr.current_url.startswith("https://recreation.utoronto.ca/registration/")):
            try:
                self.click(self.proceed_checkout_btn)
            except Exception:
                pass

            num_clicks += 1
            self.random_sleep(0.2)
