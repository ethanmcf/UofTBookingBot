import pytest
import os
from uoftbookingbot.constants import LOG_DIR_PATH, SCREENSHOTS_DIR_PATH

from uoftbookingbot.automation.logger import Logger


@pytest.fixture
def logger() -> Logger:
    return Logger()


class TestLoginManager:
    """Unit tests for the Logger class."""

    # def test_get_credentials(self, login_manager: LoginManager):
    #     username, password = login_manager.get_credentials()
    #     assert username == "test_user", f"Expected 'test_user' but got '{username}'"
    #     assert password == "test_pass", f"Expected 'test_pass' but got '{password}'"

    # def test_get_code(self, login_manager: LoginManager):
    #     code = login_manager.get_code()
    #     assert code == "123456789", f"Expected '123456789' but got '{code}'"
    #     assert (
    #         login_manager.num_codes_left() == 2
    #     ), f"Expected 2 codes left, but got {login_manager.num_codes_left()}"

    # def test_remove_code(self, login_manager: LoginManager):
    #     login_manager.get_code()  # Retrieves and removes the first code
    #     assert login_manager.num_codes_left() == 2, "Code removal failed: Expected 2 codes left"

    #     login_manager.get_code()  # Retrieves and removes the next code
    #     assert login_manager.num_codes_left() == 1, "Code removal failed: Expected 1 code left"

    # def test_num_codes_left(self, login_manager: LoginManager):
    #     assert login_manager.num_codes_left() == 3, "Initial code count should be 3"

    #     login_manager.get_code()  # Removes one code
    #     assert login_manager.num_codes_left() == 2, "Code count mismatch: Expected 2 codes left"

    # def test_save_codes(self, login_manager: LoginManager):
    #     new_codes = ["999999999", "888888888"]
    #     login_manager.save_codes(new_codes)

    #     assert (
    #         login_manager.num_codes_left() == 2
    #     ), f"Expected 2 codes left after saving, but got {login_manager.num_codes_left()}"
    #     assert login_manager.get_code() == "999999999", "First saved code mismatch"