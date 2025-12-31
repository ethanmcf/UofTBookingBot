from uoftbookingbot.activity import Activity
from uoftbookingbot.automation.constants import USER_AGENTS
from uoftbookingbot.automation.login_manager import LoginManager
from uoftbookingbot.automation.logger import Logger, LogSignaler
from uoftbookingbot.automation.flows.bypass_codes_flow import run_bypass_codes_retrieval_flow
from uoftbookingbot.automation.flows.registration_flow import run_registration_flow
from typing import Optional
import random


def run_registration_bot(
    activity: Activity,
    time_limit: int,
    codes_threshold: int,
    headless: bool,
    debug: bool,
    credentials_path: str,
    bypass_codes_path: str,
    log_path: str,
    screenshots_path: str,
    ui_signaler: Optional[LogSignaler],
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
        log_path: Path to log directory
        screenshots_path: Path to screenshots directory
    Returns:
        bool: True iff registration completed without unhandled exceptions, False otherwise.
    """

    logger = Logger(log_path, screenshots_path, ui_signaler)

    try:
        login_manager = LoginManager(credentials_path, bypass_codes_path)
        user_agent = random.choice(USER_AGENTS)

        if login_manager.num_codes_left() < codes_threshold:
            run_bypass_codes_retrieval_flow(
                login_manager=login_manager,
                logger=logger,
                user_agent=user_agent,
                headless=headless,
                debug=debug,
            )
        run_registration_flow(
            activity=activity,
            login_manager=login_manager,
            # <<<<<<< HEAD
            # =======
            # posting_offset=activity_offset,
            # >>>>>>> feature/logger
            time_limit=time_limit,
            user_agent=user_agent,
            headless=headless,
            logger=logger,
            debug=debug,
        )
    except Exception as e:
        logger.log_error(e)
        return False
    finally:
        logger.shutdown()

    return True
