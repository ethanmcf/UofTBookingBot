from typing import Callable, List, Tuple


class LoginManager:
    """Manages login credentials and bypass codes from files using safe, self-contained file operations."""

    login_file_path: str
    code_file_path: str

    def __init__(self, login_file_path: str, code_file_path: str) -> None:
        """Initializes the LoginManager with file paths."""

        self.login_file_path = login_file_path
        self.code_file_path = code_file_path

        # Validate files exist and are accessible upon initialization
        try:
            with open(self.login_file_path, "r") as f:
                f.readline()
            with open(self.code_file_path, "a+") as f:
                f.seek(0)
        except OSError as e:
            raise Exception(f"Error initializing files: {e}") from None

    def _safe_file_op(func: Callable) -> Callable:
        """Decorator to handle common file operation errors."""

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except OSError as e:
                raise Exception(f"File operation failed: {e}") from None

        return wrapper

    @_safe_file_op
    def get_credentials(self) -> Tuple[str, str]:
        """Returns (utorid, password) tuple from login file."""

        with open(self.login_file_path, "r", encoding="utf-8") as f:
            utorid = f.readline().strip()
            password = f.readline().strip()

        if not utorid or not password:
            raise Exception("Missing utorid or password in the login file.")

        return utorid, password

    @_safe_file_op
    def get_code(self) -> str:
        """Returns and removes the first bypass code from the codes file."""

        with open(self.code_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            raise Exception("No codes found in the bypass code file.")

        code_to_use = lines[0].strip()
        remaining_lines = lines[1:]
        with open(self.code_file_path, "w", encoding="utf-8") as f:
            f.writelines(remaining_lines)

        return code_to_use

    @_safe_file_op
    def num_codes_left(self) -> int:
        """Returns the number of bypass codes left in the codes file."""

        try:
            with open(self.code_file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0  # Handle case where file might be empty or deleted

    @_safe_file_op
    def save_codes(self, codes: List[str]) -> None:
        """Saves the given list of bypass codes to the codes file, overwriting existing content."""

        with open(self.code_file_path, "w", encoding="utf-8") as f:
            for code in codes:
                f.write(code.strip() + "\n")
