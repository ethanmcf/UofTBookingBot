from playwright.sync_api import Locator


def button_click_handler(locator: Locator) -> None:
    """Handler that clicks a button represented by the given locator."""

    locator.click()


def captcha_handler(locator: Locator) -> None:
    """Handler that deals with CAPTCHA."""

    print("CAPTCHA detected.")
    # locator.get_by_role("button", name="Confirm").click() # confirm button after completing captcha
