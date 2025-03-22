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
touch login.txt
echo your_username >> login.txt
echo your_password >> login.txt
```

## Usage

Once the dependencies are installed, you can run the bot to automatically sign up for UofT drop-in activities. You need to select the url and time of your choice using the provided dictionaries.

Once this is completed you can run the following command:

```bash
python3 main.py
```
