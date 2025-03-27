from selenium.webdriver.common.by import By
from Pages.BasePage import BasePage

class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_btn = (By.ID, "checkoutButton")
        self.checkout_modal_btn = (By.ID, "btnCheckoutCart")
        self.success_alert = (By.CLASS_NAME, "alert-success")

    def checkout(self):
        self.click(self.checkout_btn, sleep_params=(1, 0.3))

        self.click(self.checkout_modal_btn, sleep_params=(1, 0.3))
        
        self.find_element(self.success_alert)
        