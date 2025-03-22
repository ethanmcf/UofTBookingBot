from selenium import webdriver
from Pages.CheckoutPage import CheckoutPage
from Pages.PaymentPage import PaymentPage
from Pages.HomePage import HomePage
from Pages.SelectPage import SelectPage
from Pages.LoginPage import LoginPage
from datetime import datetime, timedelta
import time

URLS = {
    "golf" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0&semesterid=be7544c3-d05c-443f-844b-8ce87874f958",
    "hockey" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc",
}
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
    # Create and run driver with url
    dr = create_driver(True) 
    dr.get(URLS["golf"])


    home_page = HomePage(dr)
    home_page.login()
    
    login_page = LoginPage(dr)
    login_page.login()
    
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



