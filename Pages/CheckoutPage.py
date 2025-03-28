from selenium.webdriver.common.by import By
from Pages.BasePage import BasePage

class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_btn = (By.ID, "checkoutButton")
        self.checkout_modal_btn = (By.ID, "btnCheckoutCart")
        self.success_alert = (By.CLASS_NAME, "alert-success")

    def checkout(self):
        print("Checkout Page ... checking out")
        
        self.click(self.checkout_btn, sleep_params=(1, 0.3))


        self.random_sleep(3, variance=0.5)
        num_clicks = 0
        while(num_clicks < 20):
            try:
                self.dr.click(self.checkout_modal_btn)
                self.dr.find_element(self.success_alert)
                return 
            except Exception:
                pass
            
            num_clicks += 1
            self.random_sleep(0.2)

        # self.click(self.checkout_modal_btn, sleep_params=(1, 0.3))
        # self.find_element(self.success_alert)
        
        
        