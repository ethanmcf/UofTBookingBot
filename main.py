from selenium import webdriver
from Pages.CheckoutPage import CheckoutPage
from Pages.PaymentPage import PaymentPage
from Pages.HomePage import HomePage
from Pages.SelectPage import SelectPage
from Pages.LoginPage import LoginPage
from Pages.CodesPage import CodesPage
from Pages.DuoPage import DuoPage

from login_manager import LoginManager
from datetime import datetime, timedelta
import time

SPORT_URLS = {
    "golf" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0&semesterid=be7544c3-d05c-443f-844b-8ce87874f958",
    "hockey" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc",
}

BYPASS_CODES_URL = "https://bypass.utormfa.utoronto.ca/index.php"

TIMES = {
    "10AM" : ["10:00:00", "10:00 AM - 10:55 AM"],
    "11AM" : ["11:00:00", "11:00 AM - 11:55 AM"],
    "1PM" : ["13:00:00", "1:00 PM - 1:55 PM"]
}


def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr


def main():
    # Get code and reload codes if needed
    code_dr = create_driver(False)
    code_dr.get(BYPASS_CODES_URL)
    codes_page = CodesPage(code_dr)
    login_manager = LoginManager("login.txt", "bypass_codes.txt", codes_page)
    code_dr.quit()

    # Create and run driver with url
    dr = create_driver(False) 
    dr.get(SPORT_URLS["golf"])

    home_page = HomePage(dr)
    home_page.login()
    
    login_page = LoginPage(dr, login_manager)
    login_page.login()

    duo_page = DuoPage(dr, login_manager)
    duo_page.bypass()

    wanted_date = (datetime.now() + timedelta(days=2)).strftime("%A, %B %d, %Y")
    hour, times = TIMES["11AM"]
    select_time_page = SelectPage(dr, hour, times, wanted_date)
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



