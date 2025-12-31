import argparse, sys
from PyQt6.QtWidgets import QApplication
from uoftbookingbot.automation.constants import ACTIVITY_URLS
from uoftbookingbot.automation.runner import run_registration_bot
from uoftbookingbot.constants import (
    BYPASS_CODES_PATH,
    CREDENTIALS_PATH,
    LOG_DIR_PATH,
    SCREENSHOTS_DIR_PATH,
)
from uoftbookingbot.frontend.app import BookingApp


def _get_cli_args() -> argparse.Namespace:
    """Parses and returns command-line arguments."""

    # Define valid arguments structure
    parser = argparse.ArgumentParser(
        description="UofT Drop-in Activity Booking Bot. Run with no arguments to open the GUI, or with arguments to run the CLI booking script."
    )
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument("-u", "--url", help="The URL to a drop-in activity.", required=False)
    url_group.add_argument(
        "-a", "--activity", help="The name of a drop-in activity.", required=False
    )
    parser.add_argument(
        "-d",
        "--date",
        help="The date of the activity given in YYYY-MM-DD format.",
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
        help="Runs debug mode, adds screenshot and log in debug folder where exception occurs ",
        action="store_true",
    )

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


def main():
    """Main entry point for the booking bot executable. Running with no
    arguments opens the GUI, otherwise runs the CLI script."""

    if len(sys.argv) == 1:
        # Run GUI for desktop app
        qt_app = QApplication(sys.argv)

        # Create and show the main window
        window = BookingApp()
        window.setWindowTitle("UofT Booking Bot")
        window.show()

        # Run the event loop
        sys.exit(qt_app.exec())

        exit(0)

    # Run CLI script
    args = _get_cli_args()

    user_is_registered = run_registration_bot(
        activity_url=args.url,
        activity_date=args.date,
        activity_time=args.time,
        activity_offset=args.offset,
        time_limit=args.time_limit,
        codes_threshold=args.codes_threshold,
        headless=not args.visible,
        debug=args.debug,
        credentials_path=CREDENTIALS_PATH,
        bypass_codes_path=BYPASS_CODES_PATH,
        log_path=LOG_DIR_PATH,
        screenshots_path=SCREENSHOTS_DIR_PATH,
    )
    exit(0 if user_is_registered else 1)


if __name__ == "__main__":
    main()
