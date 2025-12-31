from playwright.sync_api import Page
from uoftbookingbot.automation.login_manager import LoginManager


def complete_utorid_login(login_manager: LoginManager, page: Page, recreation_login: bool) -> None:
    """Completes the UTORID login process, including MFA via bypass code."""

    # Navigate to sign-in page if logging in from recreation site
    if recreation_login:
        page.get_by_role("button", name="Sign In").click()
        page.get_by_role("button", name="school Log in with UTORID").click()

    # Sign in with UTORID
    utorid, password = login_manager.get_credentials()
    page.get_by_role("textbox", name="UTORid / JOINid").click()
    page.get_by_role("textbox", name="UTORid / JOINid").fill(utorid)
    page.locator("#password").click()
    page.locator("#password").fill(password)
    page.get_by_role("button", name="log in").click()

    # Complete multi-factor authentication (MFA)
    bypass_code = login_manager.get_code()
    page.get_by_role("link", name="Other options").click()
    page.get_by_role("link", name="Bypass code Enter a code from").click()
    page.get_by_role("textbox", name="Bypass code").click()
    page.get_by_role("textbox", name="Bypass code").fill(bypass_code)
    page.get_by_test_id("verify-button").click()
    if recreation_login:
        page.get_by_role("button", name="Yes, this is my device").click()
        page.wait_for_url("https://recreation.utoronto.ca/")
