from selenium.webdriver.common.by import By
import BasePage

class PaymentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.next_btn = (By.CLASS_NAME, "btn-NextRegistrationStep")
        self.expand_waiver_btn = (By.XPATH, "//button[@data-target='#regWaiver-collapse-1']")
        self.accept_btn = (By.CLASS_NAME, "btn-success.btnAccept")
        self.proceed_checkout_btn = (By.XPATH, "//div[contains(@class, 'stepActionButtons desktop')]//button[contains(@class, 'btn-NextRegistrationStep')]")

    def purchase(self):
        self.click(self.next_btn)
        self.click(self.expand_waiver_btn)
        self.click(self.accept_btn)
        self.click(self.proceed_checkout_btn)