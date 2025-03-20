from selenium import webdriver
from Pages.CheckoutPage import CheckoutPage
from Pages.PaymentPage import PaymentPage
from Pages.HomePage import HomePage
from Pages.SelectPage import SelectPage
import time

URLS = {
    "golf" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0&semesterid=be7544c3-d05c-443f-844b-8ce87874f958",
    "hockey" : "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc",
}
TIME = "1:00 PM - 1:55 PM"


def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr


def main():
    # Create and run driver with url
    dr = create_driver() 
    dr.get(URLS["hockey"])


    home_page = HomePage(dr)
    home_page.login()
    
    select_time_page = SelectPage(dr, TIME)
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



