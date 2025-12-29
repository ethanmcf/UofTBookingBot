import datetime
import random
from uoftbookingbot.activity import Activity
from uoftbookingbot.automation.constants import USER_AGENTS
from uoftbookingbot.automation.login_manager import LoginManager
from uoftbookingbot.automation.debugging import print_exception, get_app_logger
from uoftbookingbot.automation.flows.bypass_codes_flow import (
    run_bypass_codes_retrieval_flow,
)
from uoftbookingbot.automation.flows.registration_flow import run_registration_flow


def run_registration_bot(
    activity: Activity,
    time_limit: int,
    codes_threshold: int,
    headless: bool,
    debug: bool,
    credentials_path: str,
    bypass_codes_path: str,
    error_log_path: str,
    screenshots_path: str,
) -> bool:
    """Main entry point for running the registration bot.

    Args:
        activity: The activity to register for.
        time_limit: The maximum number of seconds to attempt registration past the start time.
        codes_threshold: The minimum number of bypass codes before fetching new ones.
        headless: Whether to run the browser in headless mode.
        debug: Whether to run in debug mode.
        credentials_path: Path to the login credentials file.
        bypass_codes_path: Path to the bypass codes file.
        error_log_path: Path to print error logs.
    Returns:
        bool: True iff registration completed without unhandled exceptions, False otherwise.
    """

    print(f"{datetime.datetime.now().isoformat()}: STARTING REGISTRATION BOT FOR {str(activity)} ")

    try:
        login_manager = LoginManager(credentials_path, bypass_codes_path)
        user_agent = random.choice(USER_AGENTS)

        if login_manager.num_codes_left() < codes_threshold:
            run_bypass_codes_retrieval_flow(
                login_manager=login_manager,
                screenshots_path=screenshots_path,
                user_agent=user_agent,
                headless=headless,
                debug=debug,
            )

        run_registration_flow(
            activity=activity,
            login_manager=login_manager,
            screenshots_path=screenshots_path,
            time_limit=time_limit,
            user_agent=user_agent,
            headless=headless,
            debug=debug,
        )
    except Exception as e:
        logger = get_app_logger(error_log_path)
        logger.exception("An unexpected error occurred.")
        print_exception(e)
        return False
    finally:
        print(f"{datetime.datetime.now().isoformat()}: ENDING REGISTRATION BOT FOR {str(activity)} ")


    return True
