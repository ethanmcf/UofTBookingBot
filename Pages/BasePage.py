from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
import random
import time

class BasePage:
    """Base page for pages to automate. Provides simple and common functions"""
    def __init__(self, driver):
        self.dr = driver
        self.wait = WebDriverWait(self.dr, 10)
    
    def quit(self):
        self.dr.quit()

    def click(self, locator, submit = False, sleep_params = None, driver_wait = None):
        if not driver_wait:
            driver_wait = self.wait
        
        btn = driver_wait.until(EC.element_to_be_clickable(locator), f"Timed out waiting for the following element to be clickable: {locator}.")

        if sleep_params:
            self.random_sleep(*sleep_params)

        if submit:
            btn.submit()
        else:
            btn.click()

        return btn
    
    def send_keys(self, locator, text, driver_wait = None): 
        if not driver_wait:
            driver_wait = self.wait

        driver_wait.until(EC.element_to_be_clickable(locator), f"Timed out waiting for the following element to be clickable: {locator}.").send_keys(text)

    def find_element(self, locator, driver_wait = None):
        if not driver_wait:
            driver_wait = self.wait
            
        return driver_wait.until(EC.visibility_of_element_located(locator), f"Timed out waiting for the following element to be visible:  {locator}.")
    
    def random_sleep(self, expected_wait, variance = 0.1):
        min_wait = max(0, expected_wait - variance)
        max_wait = max(min_wait, expected_wait + variance)
        wait_secs = random.uniform(min_wait, max_wait)
        time.sleep(wait_secs)
    
    def scroll_by(self, top = 0, left = 0):
        # Exact integer values or ranges can be passed in for scroll amounts
        if isinstance(top, tuple):
            top = random.randint(top[0], top[1])
        if isinstance(left, tuple):
            left = random.randint(left[0], left[1])

        self.dr.execute_script(
            f"window.scrollBy({{top: {top}, left: {left}, behavior: 'smooth'}});"
        )
    
    def click_repeatedly(self, locator, max_clicks = 20, init_wait_period = 0.2,
                         wait_multiplier = 1, exit_cond = None, submit = False, sleep_params = None, driver_wait = None):
        btn_to_click = locator
        wait_period = init_wait_period
        num_clicks = 0
        while(num_clicks < max_clicks):
            try:
                if isinstance(locator, tuple):
                    btn_to_click = self.click(btn_to_click, submit=submit, sleep_params=sleep_params, driver_wait=driver_wait)
                else:
                    btn_to_click.click(btn_to_click)
            except ElementClickInterceptedException as e:
                # Most likely a temporary spinner overlay -> wait it out as long as possible
                if num_clicks == max_clicks - 1:
                    # Overlay is not disappearing on time so bubble the error up
                    raise e from None
            except (NoSuchElementException, StaleElementReferenceException) as e:
                if num_clicks == 0:
                    # Error came on first click, which means it doesn't have to do
                    # with the button no longer being found due to a previous click,
                    # so re-raise the error
                    raise e from None
            
                            
            # Stop clicking if the page switched or refreshed
            if EC.invisibility_of_element(btn_to_click):
                return
            
            # Stop clicking if the custom exiting condition is met
            if callable(exit_cond) and exit_cond():
                return

            num_clicks += 1
            time.sleep(wait_period)

            # Back off time between clicks exponentially to avoid captchas
            wait_period *= wait_multiplier
