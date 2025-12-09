from playwright.sync_api import Locator, Page
from utils.captcha_solver import CaptchaSolver
import time

def button_click_handler(locator: Locator) -> None:
    """Handler that clicks a button represented by the given locator."""

    locator.click()


def captcha_handler(page: Page) -> None:
    """Handler that deals with CAPTCHA."""
    print("CAPTCHA detected, starting to solve...")

    solver = CaptchaSolver(page)
    solver.solveCaptcha() 

    page.locator("#btnReCaptchaConfirm").click()

    print("CAPTCHA solved...")

