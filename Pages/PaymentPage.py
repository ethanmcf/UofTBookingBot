from selenium.webdriver.common.by import By
from Pages.BasePage import BasePage

class PaymentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.success_count = (By.ID, 'successCount')
        self.next_btn = (By.CSS_SELECTOR, ".desktop .btn-NextRegistrationStep")
        self.expand_waiver_btn = (By.XPATH, "//button[@data-target='#regWaiver-collapse-1']")
        self.accept_btn = (By.CLASS_NAME, "btn-success.btnAccept")
        self.proceed_checkout_btn = (By.XPATH, "//div[contains(@class, 'stepActionButtons desktop')]//button[contains(@class, 'btn-NextRegistrationStep')]")
    
    def purchase(self):
        self.wait.until(lambda _: self.dr.current_url.startswith("https://recreation.utoronto.ca/registration/"),
                    f"Browser did not navigate to payment page as expected. Last URL = {self.dr.current_url}")

        if self.find_element(self.success_count).text == "1":
            print("Time slot has been secured!")
        else:
            raise Exception("Failed to secure time slot.")

        print("Payment Page ... purchasing")
        
        self.click(self.next_btn, sleep_params=(1, 0.3))

        self.click(self.expand_waiver_btn, sleep_params=(1, 0.3))

        self.click(self.accept_btn, sleep_params=(1, 0.3))

        self.random_sleep(3, variance=0.5)
        self.click_repeatedly(self.proceed_checkout_btn, init_wait_period=0.2)
