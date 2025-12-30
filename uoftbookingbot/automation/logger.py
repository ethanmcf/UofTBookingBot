import logging, os, textwrap, time, sys
from datetime import datetime, timedelta

class Logger:
    def __init__(self, log_dir: str, screenshot_dir: str):
        self.log_dir = log_dir
        self.screenshot_dir = screenshot_dir
        
        # Ensure directories exist
        for directory in [self.log_dir, self.screenshot_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        self.logger = logging.getLogger("Logger")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # INFO File for frontend access
        info_handler = logging.FileHandler(os.path.join(self.log_dir, "info.log"))
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)

        # ERROR File 
        error_handler = logging.FileHandler(os.path.join(self.log_dir, "error.log"))
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        self.logger.addHandler(info_handler)
        self.logger.addHandler(error_handler)

    def log_info(self, message: str):
        """Logs info to file and prints to console."""
        self.logger.info(message)
        print(f"[INFO]: {message}")


    def log_error(self, e: Exception):
        """Logs traceback to file and prints pretty box to console."""
        # Log full traceback 
        self.logger.exception(str(e))

        # Pretty print box for the terminal
        title = "ERROR"
        title_width = 20
        message_width = 80
        f_c, title_len = " ", len(title)
        f_len = (title_width - title_len - 2) // 2
        ex = (title_width - title_len - 2) % 2
        
        box = (
            "-" * title_width + "\n" +
            f_c * f_len + " " + title + " " + f_c * (f_len + ex) + "\n" +
            "-" * title_width + "\n" +
            textwrap.fill(str(e), width=message_width) + "\n"
        )
        print(box)

    def screenshot(self, page):
        """Saves a page screenshot and logs the path."""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(self.screenshot_dir, f"error_screenshot_{timestamp}.png")
        page.screenshot(path=screenshot_path)

        msg = f"Debug screenshot saved to: {screenshot_path}"
        self.logger.info(msg) 
        print(msg)   

    def log_countdown(self, seconds: int, wakeup_datetime):
        """Logs a ticking count down"""

        # Log every second
        while seconds > 0:
            # Format the time remaining (HH:MM:SS)
            td = timedelta(seconds=seconds)
            parts = []
            
            # Extract hours, minutes, seconds
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds_only = divmod(remainder, 60)

            if hours > 0: parts.append(f"{hours} hours")
            if minutes > 0: parts.append(f"{minutes} minutes")
            parts.append(f"{seconds_only} seconds")

            wait_str = ", ".join(parts)
            
            self.logger.info(f"[INFO]: Waiting {wait_str} until registration opens... ")

            time.sleep(1)
            seconds -= 1

        self.logger.info("[INFO]: Wakeup time reached...")        
