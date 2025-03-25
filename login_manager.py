class LoginManager():
    def __init__(self, login_file_path, code_file_path):
        self.login_file = None
        self.codes_file = None
        try:
            self.login_file = open(login_file_path, "r")
            self.codes_file = open(code_file_path, "r+")
        except OSError:
            self.cleanup()
            raise Exception("Error opening login and/or bypass codes file(s).")
        
    def cleanup_on_error(func):
        """Decorator that closes open files on error before bubbling the error up."""
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.cleanup()
                raise e from None
            
        return wrapper

    @cleanup_on_error
    def get_credentials(self):
        self.login_file.seek(0)
        username = self.login_file.readline().strip()
        password = self.login_file.readline().strip()
        if not username or not password:
            raise Exception("Missing username or password in the login file.")
        
        return username, password

    @cleanup_on_error 
    def get_code(self):
        self.codes_file.seek(0)
        code = self.codes_file.readline().strip()
        if not code:
            raise Exception("No codes found in the bypass code file.")
        self._remove_code(code)

        return code

    @cleanup_on_error
    def _remove_code(self, code):
        # Read in all codes in the file
        self.codes_file.seek(0)
        lines = self.codes_file.readlines()

        # Write all lines that aren't the given code to remove
        self.codes_file.seek(0)
        for line in lines:
            if line.strip("\n") != code.strip("\n"): 
                self.codes_file.write(line)
        
        # Ensure no other codes are kept
        self.codes_file.truncate()

    @cleanup_on_error
    def num_codes_left(self):
        self.codes_file.seek(0)
        return sum(1 for _ in self.codes_file) 

    @cleanup_on_error
    def save_codes(self, codes):        
        self.codes_file.truncate(0)
        for code in codes:
            self.codes_file.write(code + '\n')

    def cleanup(self):
        if self.login_file is not None:
            self.login_file.close()
            self.login_file = None

        if self.codes_file is not None:
            self.codes_file.close()
            self.codes_file = None
