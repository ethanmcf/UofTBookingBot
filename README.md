# UofTBookingBot 🏒

A bot that automates the sign-up process for UofT drop-in activities.

## Prerequisites

Before you begin, ensure you have Python 3.6+ and pip installed. If you don't have them, follow the instructions on the [official Python website](https://www.python.org/downloads/).

## Setup Instructions 🚀

Make sure you clone this repo first.

### 1. Create a Virtual Environment

To create a virtual environment, run the following command:

```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

To activate your virtual environment, run the following command:

```bash
source .venv/bin/activate
```

### 3. Install selenium

To install selenium, run the following command:

```bash
pip3 install -U selenium
```

### 4. Create login info

Create a file to store your username and password (in gitignore so info is not saved). Username must be on first line and password second line:

```bash
touch LoginResources/login.txt
echo your_username >> LoginResources/login.txt
echo your_password >> LoginResources/login.txt
```

## Usage

Once the dependencies are installed, you can run the bot to automatically sign up for UofT drop-in activities. You need to input the URL, date, and start time for your chosen activity using the command-line arguments `-u`, `-d`, and `-t`, respectively, as shown below:

```bash
python main.py -u ACTIVITY_URL -d YYYY-MM-DD -t HH:MM
```

Instead of passing in a URL, you can also simply pass in the name of the activity using `-a` for a select few sports. For instance, to sign up for drop-in golf on March 26th, 2025 at 11:00 AM, you would enter the following:

```bash
python main.py -a golf -d 2025-03-26 -t 11:00
```

## Advanced

There are multiple customizations available that I don't feel like explaining right now, so here is the help menu instead (found by running `python main.py -h`).

```
usage: main.py [-h] (-u URL | -a ACTIVITY) -d DATE -t TIME [-o OFFSET | --no-wait] [-l TIME_LIMIT] [-c CODES_THRESHOLD] [--visible]

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
  -l TIME_LIMIT, --time-limit TIME_LIMIT
                        The maximum number of seconds to run the bot past the start time without success. Defaults to 10.
  -c CODES_THRESHOLD, --codes-threshold CODES_THRESHOLD
                        The minimum number of codes needed before fetching new ones. Defaults to 3.
  --visible             Display the browser while running (headless by default)
```

## Testing

Install pytest:

```bash
pip3 install pytest
```

Run tests

```bash
pytest Tests/test_login_manager.py
```
