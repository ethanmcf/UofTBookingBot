from selenium.webdriver.common.by import By
import BasePage


class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_btn = (By.ID, "checkoutButton")
        self.checkout_modal_btn = (By.ID, "btnCheckoutCart")

    def checkout(self):
        self.click(self.checkout_btn)
        self.click(self.checkout_modal_btn)