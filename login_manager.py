class LoginManager():
    def __init__(self, login_file_path, code_file_path):
        self.login_file = None
        self.codes_file = None
        try:
            self.login_file = open(login_file_path, "r")
            self.codes_file = open(code_file_path, "r+")
        except:
            print("Error opening login and/or bypass codes file(s).")
            self.quit()

    def get_credentials(self):
        try:
            self.login_file.seek(0)
            username = self.login_file.readline().strip() 
            password = self.login_file.readline().strip()
            if not username or not password:
                raise Exception("Missing username or password in the login file")
            return username, password
        except:
            print("Error accessing login credentials. Ensure your login file is formatted properly")
            self.quit()

    def get_code(self):
        try:
            self.codes_file.seek(0)
            code = self.codes_file.readline().strip()
            if not code:
                raise Exception("Missing code in the bypass code file.")
            self._remove_code(code)
            return code
        except:
            print("Error getting a code from bypass codes file.")
            self.quit()

    def _remove_code(self, code):
        try:
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
        except:
            print("Error removing a code from bypass codes file.")
            self.quit()

    def num_codes_left(self):
        try:
            self.codes_file.seek(0)
            return sum(1 for _ in self.codes_file) 
        except:
            print("Error gathering number of codes left in bypass codes file.")
            self.quit()

    def save_codes(self, codes):        
        try:
            self.codes_file.truncate(0)
            for code in codes:
                self.codes_file.write(code + '\n')
        except:
            print("Error writing new codes to bypass codes file.")
            self.quit()

    def cleanup(self):
        if self.login_file is not None:
            self.login_file.close()
        if self.codes_file is not None:
            self.codes_file.close()
        
    def quit(self):
        self.cleanup()
        exit(1)
