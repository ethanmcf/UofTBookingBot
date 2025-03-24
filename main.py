from selenium import webdriver
from Pages.CheckoutPage import CheckoutPage
from Pages.PaymentPage import PaymentPage
from Pages.HomePage import HomePage
from Pages.SelectPage import SelectPage
from Pages.LoginPage import LoginPage
from Pages.CodesPage import CodesPage
from Pages.DuoPage import DuoPage
from login_manager import LoginManager
import argparse

# Global Consts
BYPASS_CODES_URL = "https://bypass.utormfa.utoronto.ca/index.php"
ACTIVITY_URLS = {
    "golf": "https://recreation.utoronto.ca/program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0",
    "soccer": "https://recreation.utoronto.ca/program/GetProgramDetails?courseId=c762f797-ce00-465f-9acd-52dc42f7eb42",
    "hockey": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc"
}

def get_args():
    # Define valid arguments structure
    parser = argparse.ArgumentParser()
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument("-u", "--url", help="The URL to a drop-in activity.", required=False)
    url_group.add_argument("-a", "--activity", help="The name of a drop-in activity.", required=False)
    parser.add_argument("-d", "--date", help="The date of the activity given in YYYY-MM-DD format.", required=True)
    parser.add_argument("-t", "--time", help="The start time of the activity given in 24-hour HH:MM format.", required=True)
    offset_group = parser.add_mutually_exclusive_group()
    offset_group.add_argument("-o", "--offset", help="The offset of how early registration opens up given in days before the start time. Defaults to 2.", type=int, default=2)
    offset_group.add_argument("--no-wait", help="Runs bot immediately rather than waiting until posting date.", action="store_true")
    parser.add_argument("-l", "--time-limit", help="The maximum number of seconds to run the bot past the start time without success. Defaults to 10.", type=int, default=10)
    parser.add_argument("-c", "--codes-threshold", help="The minimum number of codes needed before fetching new ones. Defaults to 3.", type=int, default=3)
    parser.add_argument("--visible", help="Display the browser while running (headless by default)", action="store_true")

    # Get args from command-line
    args = parser.parse_args()

    # Get activity url from known activities if a key name was given instead of a url
    if args.activity:
        args.url = ACTIVITY_URLS.get(args.activity)
        if not args.url:
            print("Invalid drop-in activity given.")
            exit(2)
    
    # Nullify posting offset if no wait flag was given
    if args.no_wait:
        args.offset = None

    return args

def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    if headless: option.add_argument('headless')
    dr = webdriver.Chrome(options=option)
    return dr

def run_fetch_bypass_codes(headless, login_manager):
    # Fetch new bypass codes
    print("Fetching new bypass codes...")

    codes_dr = create_driver(headless)
    codes_dr.get(BYPASS_CODES_URL)

    codes_login_page = LoginPage(codes_dr, login_manager)
    codes_login_page.login()

    codes_duo_page = DuoPage(codes_dr, login_manager, has_trust_prompt=False)
    codes_duo_page.bypass()

    codes_page = CodesPage(codes_dr, login_manager)
    codes_page.generate_codes()

    codes_dr.quit()

    print("Successfully saved new bypass codes.")

def run_bot(headless, login_manager, url, date, start_time, posting_offset, time_limit):
    # Register for drop-in activity
    print("Setting up registration for drop-in activity...")
    
    dr = create_driver(headless) 
    dr.get(url)

    home_page = HomePage(dr)
    home_page.login()
    
    login_page = LoginPage(dr, login_manager)
    login_page.login()

    duo_page = DuoPage(dr, login_manager)
    duo_page.bypass()

    select_time_page = SelectPage(dr, date, start_time, posting_offset, time_limit)
    select_time_page.select()

    payment_page = PaymentPage(dr)
    payment_page.purchase()

    check_out_page = CheckoutPage(dr)
    check_out_page.checkout()

    dr.quit()

    print("Successfully finished registration.")
    
def main():
    # Gather registration data input from command-line
    args = get_args()

    # Create login manager for credential handling
    login_manager = LoginManager("LoginResources/login.txt", "LoginResources/bypass_codes.txt")

    try:
        # Fetch new codes if at or below threshold
        headless = not args.visible
        if login_manager.num_codes_left() <= args.codes_threshold:
            run_fetch_bypass_codes(headless, login_manager)
        
        # Run bot
        run_bot(headless, login_manager, args.url, args.date, args.time, args.offset, args.time_limit)

        # Cleanup resources used by login manager
        login_manager.cleanup()
    except Exception as e:
        print(e)
        exit(1)
    finally:
        login_manager.cleanup()
   
if __name__ == '__main__':
    main()
