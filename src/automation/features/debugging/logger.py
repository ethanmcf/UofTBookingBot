import logging
import os


def get_app_logger(debug_folder_path: str):
    """Configures and returns the application logger."""

    log_folder = os.path.join(debug_folder_path, "logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(log_folder, "error.log"),
        filemode="a",
    )

    return logging.getLogger()
