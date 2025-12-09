# UofTBookingBot 🏒

A bot that automates the sign-up process for UofT drop-in activities.

## Prerequisites

Before you begin, ensure you have Python 3.11.1+ and pip installed. If you don't have them, follow the instructions on the [official Python website](https://www.python.org/downloads/).

## Setup Instructions 🚀

### Start by cloning this repo:

```bash
git clone https://github.com/ethanmcf/UofTBookingBot.git
cd UoftBookingBot
```

### Run setup script

This script will create a virtual env, install dependencies and create secrets files. Secret files
are in gitignore so they will not be commited.

```bash
chmod +x scripts/setup.sh && ./scripts/setup.sh your_utorid your_password
source .venv/bin/activate # activate virtual environment
```

Make sure to select the correct interpreter befor running.

### 5. Generate bypass codes

You must also manually generate a list of DUO Mobile (MFA) bypass codes and place them in `secrets/bypass_codes.txt` This only has to do be done once as the bot will automatically regenerate them after the first the run when needed. Each code should be on its own line, e.g.:

```txt
111111111
222222222
333333333
```

## Usage

Once the dependencies are installed, you can run the bot to automatically sign up for UofT drop-in activities. You need to input the URL, date, and start time for your chosen activity using the command-line arguments `-u`, `-d`, and `-t`, respectively, as shown below:

```bash
python src/register.py -u ACTIVITY_URL -d YYYY-MM-DD -t HH:MM
```

Instead of passing in a URL, you can also simply pass in the name of the activity using `-a` for a select few sports. For instance, to sign up for drop-in golf on March 26th, 2025 at 11:00 AM, you would enter the following:

```bash
python src/register.py -a golf -d 2025-03-26 -t 11:00
```

## Advanced

There are multiple customizations available that I don't feel like explaining right now, so here is the help menu instead (found by running `python src/register.py -h`).

```
usage: register.py [-h] (-u URL | -a ACTIVITY) -d DATE -t TIME [-o OFFSET | --no-wait] [-c CODES_THRESHOLD] [-l TIME_LIMIT] [--visible]
                   [--debug]

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     The URL to a drop-in activity.
  -a ACTIVITY, --activity ACTIVITY
                        The name of a drop-in activity.
  -d DATE, --date DATE  The date of the activity given in YYYY-MM-DD format.
  -t TIME, --time TIME  The start time of the activity given in 24-hour HH:MM format.
  -o OFFSET, --offset OFFSET
                        The offset of how early registration opens up given in days before the start time. Defaults to 2.
  --no-wait             Runs bot immediately rather than waiting until posting date.
  -c CODES_THRESHOLD, --codes-threshold CODES_THRESHOLD
                        The minimum number of codes needed before fetching new ones. Defaults to 3.
  -l TIME_LIMIT, --time-limit TIME_LIMIT
                        The maximum number of seconds to run the bot past the start time without success. Defaults to 10.
  --visible             Display the browser while running (headless by default)
  --debug               Runs debug mode, adds screenshot in debug folder where exception occurs
```

## Testing

To run tests:

```bash
python -m Tests.utils.test_captcha_handler
```

Tests can be found in the `tests` folder.
