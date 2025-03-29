from selenium import webdriver
from Pages.CheckoutPage import CheckoutPage
from Pages.PaymentPage import PaymentPage
from Pages.HomePage import HomePage
from Pages.SelectPage import SelectPage
from Pages.LoginPage import LoginPage
from Pages.CodesPage import CodesPage
from Pages.DuoPage import DuoPage
import textwrap

from selenium.common.exceptions import TimeoutException
from login_manager import LoginManager
import argparse, random, os
from datetime import datetime

# Global Consts
BYPASS_CODES_URL = "https://bypass.utormfa.utoronto.ca/index.php"
ACTIVITY_URLS = {
    "golf": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=5904837f-6aa4-4707-bcfb-2ece4049bae0",
    "soccer": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=c762f797-ce00-465f-9acd-52dc42f7eb42",
    "hockey": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=dcd5a035-731e-416b-a546-5f808404a3dc",
    "basketball": "https://recreation.utoronto.ca/Program/GetProgramDetails?courseId=56e18068-7b50-45df-8854-1921ad1bee80"
}
AGENTS = [
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
]

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
    parser.add_argument("--debug", help="Runs debug mode, adds screenshot in debug folder where exception occurs ", action="store_true")


    # Get args from command-line
    args = parser.parse_args()

    # Get activity url from known activities if a key name was given instead of a url
    if args.activity:
        args.url = ACTIVITY_URLS.get(args.activity)
        if not args.url:
            raise Exception("Invalid drop-in activity given.")
    
    # Nullify posting offset if no wait flag was given
    if args.no_wait:
        args.offset = None

    return args

def random_agent():
    return random.choice(AGENTS)

def create_driver(headless = False):
    option = webdriver.ChromeOptions()
    
    # Set agent
    agent = random_agent()
    option.add_argument(f'--user-agent={agent}')

    # Turn on logs for fetch request detection
    option.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    # Ensure extensions don't interfere with our bot
    option.add_argument('--disable-extensions')

    # Choose whether to show the browser or not visually
    if headless:
        option.add_argument('headless')

    # Add anti-automation options to reduce liklihood of triggering captchas
    option.add_argument('--start-maximized')
    option.add_argument("--disable-blink-features=AutomationControlled") 
    option.add_experimental_option("useAutomationExtension", False) 
    option.add_experimental_option("excludeSwitches", ["enable-automation"]) 

    # Create a Google Chrome browser
    dr = webdriver.Chrome(options=option)

    # Clear JS properties that indicate we are a bot
    dr.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 

    return dr

def run_fetch_bypass_codes(dr, login_manager):
    # Fetch new bypass codes
    print("Fetching new bypass codes... \n" + "-"*30)

    dr.get(BYPASS_CODES_URL)

    codes_login_page = LoginPage(dr, login_manager)
    codes_login_page.login()

    try:
        codes_duo_page = DuoPage(dr, login_manager, has_trust_prompt=False)
        codes_duo_page.bypass()
    except TimeoutException as e:
        if not dr.current_url.startswith("https://recreation.utoronto.ca/"):
            raise e

    codes_page = CodesPage(dr, login_manager)
    codes_page.generate_codes()

    print("Successfully saved new bypass codes. \n")

def run_bot(dr, login_manager, url, date, start_time, posting_offset, time_limit):
    # Register for drop-in activity
    print("Setting up registration for drop-in activity...\n" + "-"*50)
    
    dr.get(url)

    home_page = HomePage(dr)
    home_page.login()
    
    login_page = LoginPage(dr, login_manager)
    login_page.login()

    duo_page = DuoPage(dr, login_manager)
    try:
        # DUO page doesn't always show up at this point -> Bypass if it does
        duo_page.bypass()
    except TimeoutException as e:
        # Timeout is expected if DUO page didn't show up, unknown error otherwise
        if not dr.current_url.startswith("https://recreation.utoronto.ca/"):
            raise e from None

    select_time_page = SelectPage(dr, date, start_time, posting_offset, time_limit)
    select_time_page.select()

    payment_page = PaymentPage(dr)
    payment_page.purchase()

    check_out_page = CheckoutPage(dr)
    check_out_page.checkout()

    print("Successfully finished registration. \n")

def print_exception(e):
    title = "ERROR"
    title_width = 35
    message_width = 80  # max width
    f_c = " "  # fill char in title
    title_len = len(title)
    f_len = (title_width - title_len - 2) // 2  # number of fill chars on each side
    ex = (title_width - title_len - 2) % 2  # extra fill char on right side if nec.
    print(
        "-" * title_width + "\n" +
        f_c * f_len + " " + title + " " + f_c * (f_len + ex) + "\n" + 
        "-" * title_width + "\n" +
        textwrap.fill(str(e), width=message_width) + "\n"
    )

def create_debug_folder():
        folder_path = "Debug" 

        # Check if folder exists
        if not os.path.exists(folder_path):
            # Folder doesn't exist, create it
            os.makedirs(folder_path)
def main():
    login_manager = None
    driver = None

    try:
        # Gather registration data input from command-line
        args = get_args()

        # Create login manager for credential handling
        login_manager = LoginManager("LoginResources/login.txt", "LoginResources/bypass_codes.txt")

        # Fetch new codes if at or below threshold
        headless = not args.visible 
        if login_manager.num_codes_left() <= args.codes_threshold:
            driver = create_driver(headless)
            run_fetch_bypass_codes(driver, login_manager)
            driver.quit()
        
        # Run bot
        driver = create_driver(headless)
        run_bot(driver, login_manager, args.url, args.date, args.time, args.offset, args.time_limit)
    except Exception as e:
        if args.debug:
            create_debug_folder()
            timestamp = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
            driver.save_screenshot(f"Debug/exception{timestamp}.png")
        print_exception(e)
        exit(1)
    finally:
        # Cleanup resources
        if driver:
            driver.quit()
        if login_manager:
            login_manager.cleanup()
    
    exit(0)
   
if __name__ == '__main__':
    main()
