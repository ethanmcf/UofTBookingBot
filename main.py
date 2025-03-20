from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from datetime import datetime, timedelta
import time


data = {
    # "URL": "https://recreation.utoronto.ca/program/getprogramdetails?courseid=5904837f-6aa4-4707-bcfb-2ece4049bae0&semesterid=be7544c3-d05c-443f-844b-8ce87874f958",
    'URL' : 'https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc',
}

class BasePage:
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def run_driver(self):
        self.dr.get(self.url)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator):
        try: 
            btn = self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print("Timeout")
            self.quit()
        btn.click()
    
    def send_keys(self, locator, text):
        try: 
            field = self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print("Timeout")
            self.quit()
        field.send_keys(text)

class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.login_btn = (By.ID,'loginLinkBtn')
        self.uoft_login_btn_pu = (By.CLASS_NAME, "btn-sso-shibboleth")
    
    def wait_for_url_to_start(self):
        try:
            WebDriverWait(self.dr, 60).until(
                lambda driver: driver.current_url.startswith("https://recreation.utoronto.ca/")
            )
        except:
            print("Took too long to login")
            self.quit()

    def login(self):
        self.click(self.login_btn)
        self.click(self.uoft_login_btn_pu)

        # Allow 60 timeout for manual login
        self.wait_for_url_to_start()


class SelectTimePage(BasePage):
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
        
        if not card:
            print("Error getting card")
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

    

class PaymentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.next_btn = (By.CLASS_NAME, "btn-NextRegistrationStep")
        self.expand_waiver_btn = (By.XPATH, "//button[@data-target='#regWaiver-collapse-1']")
        self.accept_btn = (By.CLASS_NAME, "btn-success.btnAccept")
        self.checkout_btn = (By.XPATH, "//div[contains(@class, 'stepActionButtons desktop')]//button[contains(@class, 'btn-NextRegistrationStep')]")

    def purchase(self):
        self.click(self.next_btn)
        self.click(self.expand_waiver_btn)
        self.click(self.accept_btn)
        self.click(self.checkout_btn)

class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_btn = (By.ID, "checkoutButton")
        self.checkout_modal_btn = (By.ID, "btnCheckoutCart")

    def checkout(self):
        self.click(self.checkout_btn)
        self.click(self.checkout_modal_btn)

def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr


def main():
    dr = create_driver() 
    dr.get(data["URL"])
    home_page = HomePage(dr)
    home_page.login()
    
    select_time_page = SelectTimePage(dr, "1:00 PM - 1:55 PM") # Set time wanted needs to be exact
    select_time_page.select()

    payment_page = PaymentPage(dr)
    payment_page.purchase()

    check_out_page = CheckoutPage(dr)
    check_out_page.checkout()

    print("done")
    time.sleep(5)
    
    dr.quit()



if __name__ == '__main__':
    main()



