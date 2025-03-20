from BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

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