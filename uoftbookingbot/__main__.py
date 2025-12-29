import argparse
import sys
from uoftbookingbot.automation.constants import ACTIVITY_IDS
from uoftbookingbot.automation.runner import run_registration_bot
from uoftbookingbot.constants import (
    BYPASS_CODES_PATH,
    CREDENTIALS_PATH,
    ERROR_LOG_PATH,
    SCREENSHOTS_PATH,
)


def _get_cli_args() -> argparse.Namespace:
    """Parses and returns command-line arguments."""

    # Define valid arguments structure
    parser = argparse.ArgumentParser(
        description="UofT Drop-in Activity Booking Bot. Run with no arguments to open the GUI, or with arguments to run the CLI booking script."
    )
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument("-i", "--activity-id", help="The ID of a drop-in activity.", required=False)
    url_group.add_argument(
        "-a", "--activity-name", help="The name of a drop-in activity.", required=False
    )
    parser.add_argument(
        "-d",
        "--date",
        help="The start date of the activity given in YYYY-MM-DD format.",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--time",
        help="The start time of the activity given in 24-hour HH:MM format.",
        required=True,
    )
    offset_group = parser.add_mutually_exclusive_group()
    offset_group.add_argument(
        "-o",
        "--offset",
        help="The offset of how early registration opens up given in days before the start time. Defaults to 2.",
        type=int,
        default=2,
    )
    offset_group.add_argument(
        "--no-wait",
        help="Runs bot immediately rather than waiting until posting date.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--codes-threshold",
        help="The minimum number of codes needed before fetching new ones. Defaults to 3.",
        type=int,
        default=3,
    )
    parser.add_argument(
        "-l",
        "--time-limit",
        help="The maximum number of seconds to run the bot past the start time without success. Defaults to 10.",
        type=int,
        default=10,
    ),
    parser.add_argument(
        "--visible",
        help="Display the browser while running (headless by default)",
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Runs debug mode, adds screenshot in debug folder where exception occurs ",
        action="store_true",
    )

    # Get args from command-line
    args = parser.parse_args()

    # Get activity id from known activities if a key name was given instead of an id
    if args.activity_name:
        args.activity_id = ACTIVITY_IDS.get(args.activity_name)
        if not args.activity_id:
            raise Exception("Invalid drop-in activity given.")

    # Nullify posting offset if no wait flag was given
    if args.no_wait:
        args.offset = None

    return args


def main():
    """Main entry point for the booking bot executable. Running with no
    arguments opens the GUI, otherwise runs the CLI script."""

    if len(sys.argv) == 1:
        # Run GUI for desktop app
        print("Run GUI here...")
        sys.exit(0)

    # Run CLI script
    args = _get_cli_args()
    user_is_registered = run_registration_bot(
        activity_id=args.activity_id,
        activity_date=args.date,
        activity_time=args.time,
        activity_offset=args.offset,
        time_limit=args.time_limit,
        codes_threshold=args.codes_threshold,
        headless=not args.visible,
        debug=args.debug,
        credentials_path=CREDENTIALS_PATH,
        bypass_codes_path=BYPASS_CODES_PATH,
        error_log_path=ERROR_LOG_PATH,
        screenshots_path=SCREENSHOTS_PATH,
    )
    sys.exit(0 if user_is_registered else 1)


if __name__ == "__main__":
    main()
