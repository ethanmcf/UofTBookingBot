import argparse, sys
from uoftbookingbot.activity import Activity
from uoftbookingbot.constants import ACTIVITIES
from uoftbookingbot.automation.runner import run_registration_bot
from uoftbookingbot.frontend.app import run_app
from uoftbookingbot.scheduling.api import get_scheduler


def _get_cli_args() -> argparse.Namespace:
    """Parses and returns command-line arguments."""

    # Define valid arguments structure
    parser = argparse.ArgumentParser(
        description="UofT Drop-in Activity Booking Bot. Run with no arguments to open the GUI, or with arguments to run the CLI booking script."
    )
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument(
        "-i", "--activity-id", help="The ID of a drop-in activity.", required=False
    )
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
    offset_group = parser.add_mutually_exclusive_group(required=False)
    offset_group.add_argument(
        "-o",
        "--offset",
        help="The offset of how early registration opens up given in days before the start time.",
        type=int,
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

    # Validate activity id and posting offset args:
    #  - Must ensure that activity id is given either directly or via known activity name
    #  - Must ensure that posting offset is given either directly, via known activity, or no-wait flag
    #  - Posting offset cannot be negative if given
    offset = None
    if args.activity_name:
        # Get desired activity from known activities
        desired_activity = ACTIVITIES.get(args.activity_name)
        if desired_activity is None:
            raise Exception("Invalid drop-in activity given.")

        # Use activity id from known activity
        args.activity_id = desired_activity.get("id")
        if args.activity_id is None:
            raise Exception("No activity ID found for given activity name.")

        # Use saved offset for activity if no offset given
        if args.offset is None and not args.no_wait:
            if "posting_offset" not in desired_activity:
                raise Exception(
                    "No offset given and no saved offset for activity. Please provide a posting offset or use the --no-wait flag."
                )
            offset = desired_activity.get("posting_offset")
    elif args.offset is None and not args.no_wait:
        # No activity name given to look up offset, and no offset or no-wait flag given
        raise Exception(
            "No offset given. Please provide a posting offset or use the --no-wait flag."
        )
    elif args.offset is not None and args.offset < 0:
        raise Exception("Offset cannot be negative.")

    # Set the final posting offset value to use
    if args.offset is not None:
        offset = args.offset
    args.offset = offset

    return args


def main():
    """Main entry point for the booking bot executable. Running with no
    arguments opens the GUI, otherwise runs the CLI script."""

    if len(sys.argv) == 1:
        # Clean up any old or expired scheduled bookings
        get_scheduler().cleanup_expired_schedules()

        # Run GUI for desktop app
        run_app()
        return

    # Run CLI script
    args = _get_cli_args()
    activity_to_book = Activity(
        id=args.activity_id,
        start_date=args.date,
        start_time=args.time,
        posting_offset=args.offset,
    )

    try:
        run_registration_bot(
            activity=activity_to_book,
            time_limit=args.time_limit,
            codes_threshold=args.codes_threshold,
            headless=not args.visible,
            debug=args.debug,
            ui_signaler=None,
        )
    except Exception:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
