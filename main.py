from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


data = {
    "URL": "https://recreation.utoronto.ca/program/getprogramdetails?courseid=5904837f-6aa4-4707-bcfb-2ece4049bae0&semesterid=be7544c3-d05c-443f-844b-8ce87874f958",
    'utroid': '',
    'password' : '',
}

class BasePage:
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def run_driver(self):
        self.dr.get(self.url)
    
    def quit(self):
        self.dr.quit()

    def wait_for(self, locator):
        try: 
            obj = self.wait.until(EC.visibility_of_element_located(locator))
            return obj
        except TimeoutException:
            print("Timeout")
            self.quit()

    def click(self, locator):
        btn = self.wait_for(locator)
        btn.click()
    
    def send_keys(self, locator, text):
        field = self.wait_for(locator)
        field.send_keys(text)

class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.login_btn = (By.ID,'loginLinkBtn')
        self.uoft_login_btn_pu = (By.CLASS_NAME, "btn-sso-shibboleth")
    
    def login(self):
        self.click(self.login_btn)
        self.click(self.uoft_login_btn_pu)

        # Allow 60 timeout for manual login
        def is_element_present(locator):
            try:
                self.dr.find_element(By.XPATH, "//h1[contains(text(), 'Drop in Golf Driving Range')]") # Checks if page content is loaded
                return True
            except:
                return False
        
        start_time = time.time()
        while time.time() - start_time < 60:
            if is_element_present((By.ID, "logoutForm")): 
                return


class SelectTimePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.time_slot_cards = (By.CLASS_NAME, '.program-instance-card')
        self.select_btn = (By.CLASS_NAME, '.btn btn-outline-primary program-select-btn w-100 mb-2')
    
    def wait_for_all(self, locator):
        try: 
            obj = self.wait.until(EC.visibility_of_all_elements_located(locator))
            return obj
        except TimeoutException:
            print("Timeout")
            self.quit()

    def select(self):
        cards = self.wait_for_all(self.time_slot_cards)
        for card in cards:
            time_element = card.find_element(By.CSS_SELECTOR, '.instance-time-header')
            time_text = time_element.text.strip() 

            if time_text == "11:00 AM - 11:55 AM":
                btn = card.find_element(By.CSS_SELECTOR, '.btn.btn-outline-primary.program-select-btn')
                btn.click()

    
    def trust_browser(self):
        self.click(self.trust_btn)

class CheckoutPage(BasePage):
    pass

def create_driver(headless):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr


def main():
    dr = create_driver(False)
    dr.get(data["URL"])
    home_page = HomePage(dr)
    home_page.login()
    
    # Wait until Manual login
        # time.sleep(1)
    # WebDriverWait(dr, 1000000).until(
    #     EC.visibility_of_element_located(dr.find_element(By.ID, "logoutForm"))
    # )

    
    print("done")
    dr.quit()



if __name__ == '__main__':
    main()



