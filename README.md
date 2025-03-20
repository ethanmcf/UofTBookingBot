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

## Usage
Once the dependencies are installed, you can run the bot to automatically sign up for UofT drop-in activities. You will have 60 seconds to mannualy log in with your UTORid and complete the two factor authentication and then the bot will continue.
You also need to set the url at the top of the file with the drop in sport of your choice as well as the exact time you want your drop in sport.

Once this is completed you can run the following command:
```bash
python3 main.py
```

