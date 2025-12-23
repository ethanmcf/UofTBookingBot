import random
from typing import Optional
from src.automation.features.shared.config import USER_AGENTS
from src.automation.features.credentials.login_manager import LoginManager
from src.automation.features.debugging.helpers import print_exception
from src.automation.features.debugging.logger import get_app_logger
from src.automation.flows.bypass_codes_retrieval_flow import run_bypass_codes_retrieval_flow
from src.automation.flows.registration_flow import run_registration_flow


def run_registration_bot(
    activity_url: str,
    activity_date: str,
    activity_time: str,
    activity_offset: Optional[int],
    time_limit: int,
    codes_threshold: int,
    headless: bool,
    debug: bool,
    secrets_folder_path: str,
    debug_folder_path: str,
) -> bool:
    """Main entry point for running the registration bot.

    Args:
        activity_url: The URL to the drop-in activity.
        activity_date: The date of the activity in YYYY-MM-DD format.
        activity_time: The start time of the activity in HH:MM format.
        activity_offset: The number of days before the activity that registration opens.
        time_limit: The maximum number of seconds to attempt registration past the start time.
        codes_threshold: The minimum number of bypass codes before fetching new ones.
        headless: Whether to run the browser in headless mode.
        debug: Whether to run in debug mode.
        secrets_folder_path: Path to the folder containing secret files.
        debug_folder_path: Path to the folder for saving debug information.
    Returns:
        bool: True iff registration completed without unhandled exceptions, False otherwise.
    """

    try:
        login_manager = LoginManager(
            f"{secrets_folder_path}/login_credentials.txt",
            f"{secrets_folder_path}/bypass_codes.txt",
        )
        user_agent = random.choice(USER_AGENTS)

        if login_manager.num_codes_left() < codes_threshold:
            run_bypass_codes_retrieval_flow(
                login_manager=login_manager,
                debug_folder_path=debug_folder_path,
                user_agent=user_agent,
                headless=headless,
                debug=debug,
            )

        run_registration_flow(
            program_url=activity_url,
            date=activity_date,
            time=activity_time,
            login_manager=login_manager,
            debug_folder_path=debug_folder_path,
            posting_offset=activity_offset,
            time_limit=time_limit,
            user_agent=user_agent,
            headless=headless,
            debug=debug,
        )
    except Exception as e:
        if debug:
            logger = get_app_logger(debug_folder_path)
            logger.exception("An unexpected error occurred.")
        print_exception(e)
        return False

    return True
