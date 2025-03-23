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

# Global Consts
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

CODE_THRESHOLD = 3

def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr

def run_fetch_bypass_codes(login_manager):
    # Fetch new bypass codes
    print("Fetching new bypass codes...")

    codes_dr = create_driver(headless=False)
    codes_dr.get(BYPASS_CODES_URL)

    codes_login_page = LoginPage(codes_dr, login_manager)
    codes_login_page.login()

    codes_duo_page = DuoPage(codes_dr, login_manager, has_trust_prompt=False)
    codes_duo_page.bypass()

    codes_page = CodesPage(codes_dr, login_manager)
    codes_page.generate_codes()

    codes_dr.quit()

    print("Successfully saved new bypass codes.")

def run_bot(login_manager):
     # Register for drop-in activity
    print("Setting up registration for drop-in activity...")
    
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

    print("Successfully finished registration.")
    
    dr.quit()

def main():
    # Create login manager for credential handling
    login_manager = LoginManager("login.txt", "bypass_codes.txt")

    # Fetch new codes if falling below threshold
    if login_manager.num_codes_left() <= CODE_THRESHOLD:
        run_fetch_bypass_codes()
    
    # Run bot
    run_bot(login_manager)
   


if __name__ == '__main__':
    main()



