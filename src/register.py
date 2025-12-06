import random
from utils.cli import get_cli_args
from utils.constants import LOGIN_CREDENTIALS_PATH, BYPASS_CODES_PATH, USER_AGENTS
from utils.login_manager import LoginManager
from utils.debug_helpers import print_exception
from flows.bypass_codes_retrieval_flow import run_bypass_codes_retrieval_flow
from flows.registration_flow import run_registration_flow


if __name__ == "__main__":
    try:
        args = get_cli_args()
        login_manager = LoginManager(LOGIN_CREDENTIALS_PATH, BYPASS_CODES_PATH)
        user_agent = random.choice(USER_AGENTS)

        if login_manager.num_codes_left() < args.codes_threshold:
            run_bypass_codes_retrieval_flow(
                login_manager=login_manager,
                user_agent=user_agent,
                headless=args.visible == False,
                debug=args.debug,
            )

        run_registration_flow(
            program_url=args.url,
            date=args.date,
            time=args.time,
            login_manager=login_manager,
            posting_offset=args.offset,
            time_limit=args.time_limit,
            user_agent=user_agent,
            headless=args.visible == False,
            debug=args.debug,
        )
    except Exception as e:
        print_exception(e)
        exit(1)

    exit(0)
