import os
import pytest
import os
from dotenv import load_dotenv
from src.utils.login_manager import LoginManager


@pytest.fixture
def login_manager() -> LoginManager:
    load_dotenv()

    # Create folder and files if they do not exist
    folder_path = os.getenv("TEST_RESOURCES_PATH", "./tests/resources")
    if not os.path.exists(folder_path):
        # Folder doesn't exist, create it
        os.makedirs(folder_path)

    # Temporary file paths for testing
    login_file = f"{folder_path}/login_test.txt"
    code_file = f"{folder_path}/bypass_codes_test.txt"

    # Write initial login credentials
    with open(login_file, "w") as f:
        f.write("test_user\n")
        f.write("test_pass\n")

    # Write initial bypass codes
    with open(code_file, "w") as f:
        f.write("123456789\n")
        f.write("987654321\n")
        f.write("111222333\n")

    return LoginManager(login_file_path=login_file, code_file_path=code_file)


class TestLoginManager:
    """Unit tests for the LoginManager class."""

    def test_get_credentials(self, login_manager: LoginManager):
        username, password = login_manager.get_credentials()
        assert username == "test_user", f"Expected 'test_user' but got '{username}'"
        assert password == "test_pass", f"Expected 'test_pass' but got '{password}'"

    def test_get_code(self, login_manager: LoginManager):
        code = login_manager.get_code()
        assert code == "123456789", f"Expected '123456789' but got '{code}'"
        assert (
            login_manager.num_codes_left() == 2
        ), f"Expected 2 codes left, but got {login_manager.num_codes_left()}"

    def test_remove_code(self, login_manager: LoginManager):
        login_manager.get_code()  # Retrieves and removes the first code
        assert (
            login_manager.num_codes_left() == 2
        ), "Code removal failed: Expected 2 codes left"

        login_manager.get_code()  # Retrieves and removes the next code
        assert (
            login_manager.num_codes_left() == 1
        ), "Code removal failed: Expected 1 code left"

    def test_num_codes_left(self, login_manager: LoginManager):
        assert login_manager.num_codes_left() == 3, "Initial code count should be 3"

        login_manager.get_code()  # Removes one code
        assert (
            login_manager.num_codes_left() == 2
        ), "Code count mismatch: Expected 2 codes left"

    def test_save_codes(self, login_manager: LoginManager):
        new_codes = ["999999999", "888888888"]
        login_manager.save_codes(new_codes)

        assert (
            login_manager.num_codes_left() == 2
        ), f"Expected 2 codes left after saving, but got {login_manager.num_codes_left()}"
        assert login_manager.get_code() == "999999999", "First saved code mismatch"
