class CaptchaSolverFailedError(Exception):
    """Exception raised when captcha solving fails."""

    def __init__(self, message):
        super().__init__(f"CAPTCHA SOLVER FAILED: {message}")
