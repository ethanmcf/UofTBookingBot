from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Pages.BasePage import BasePage

class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_btn = (By.ID, "checkoutButton")
        self.checkout_modal = (By.ID, "CheckoutModal")
        self.checkout_modal_btn = (By.ID, "btnCheckoutCart")
        self.success_alert = (By.CLASS_NAME, "alert-success")

    def checkout(self):
        print("Checkout Page ... checking out")
        
        self.click_repeatedly(self.checkout_btn, max_clicks=20, init_wait_period=0.4, wait_multiplier=1.25, sleep_params=(2, 0.3), 
                              exit_cond= lambda: EC.visibility_of_element_located(self.checkout_modal))
        self.random_sleep(2, variance=0.5)
        self.click_repeatedly(self.checkout_modal_btn, init_wait_period=0, sleep_params=(1, 0.3))
        
        self.find_element(self.success_alert)
           