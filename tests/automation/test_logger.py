import pytest
from unittest.mock import MagicMock
from pathlib import Path
from uoftbookingbot.automation.logger import Logger


@pytest.fixture
def magic_mock_page():
    """Simulates a Playwright Page object."""
    mock_page = MagicMock()

    def side_effect(path):
        with open(path, "w") as f:
            f.write("fake image data")

    mock_page.screenshot.side_effect = side_effect
    return mock_page


@pytest.fixture
def logger_setup() -> Logger:
    folder_dir = "./tests/logs"
    screenshot_dir = "./tests/screenshots"
    return Logger(folder_dir, screenshot_dir, name="TestLogger"), folder_dir, screenshot_dir


class TestLogger:
    """Unit tests for the Logger class."""

    def test_info_log(self, logger_setup):
        logger, log_dir, _ = logger_setup
        msg = "Test messsage"
        logger.log_info(msg)

        info_file = Path(log_dir) / "info.log"
        assert info_file.exists()
        assert msg in info_file.read_text()

    def test_error_log(self, logger_setup):
        logger, log_dir, _ = logger_setup
        error_message = "Test error"

        try:
            raise ValueError(error_message)
        except ValueError as e:
            logger.log_error(e)

        error_file = Path(log_dir) / "error.log"
        info_file = Path(log_dir) / "info.log"

        # Check if error exists in BOTH files
        assert error_file.exists()
        assert error_message in error_file.read_text()
        assert error_message in info_file.read_text()

    def test_screenshot(self, logger_setup, magic_mock_page):
        logger, _, screenshot_dir = logger_setup
        expected_num_screenshots = len(list(Path(screenshot_dir).glob("*.png"))) + 1

        logger.screenshot(magic_mock_page)

        # Check if a .png file was created in the screenshot directory
        screenshots = list(Path(screenshot_dir).glob("*.png"))
        assert len(screenshots) == expected_num_screenshots
        assert "error_screenshot_" in screenshots[0].name
