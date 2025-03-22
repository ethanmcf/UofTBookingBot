class LoginManager():
    def __init__(self, BYPASS_CODES_URL, login_file_path, code_file_path):
        self.login_file_path = login_file_path
        self.code_file_path = code_file_path
        self.BYPASS_CODES_URL = BYPASS_CODES_URL

    def get_credentials(self):
        try:
            with open(self.login_file_path, 'r') as file:
                username = file.readline().strip() 
                password = file.readline().strip()
                if not username or not password:
                    raise Exception("Missing username or password in the login file")
                return username, password  
        except:
            print("Error with login file")
            self.quit()


    # Assumes at least one code in file
    def get_code(self):
        try:
            with open(self.code_file_path, 'r') as file:
                code = file.readline().strip()
                if not code:
                    raise Exception("Missing code in the bypass code file")
                
                # No more codes - reload them
                if file.readline().strip() == "":
                    self._retreive_codes()
                
                return code
        except:
            print("Error with bypass code file")
            self.quit()

    def _retreive_codes(self):
        try:
            with open(self.code_file_path, 'w') as file:
                file.write("")
        except:
            print("Error writing to bypass code file")
            self.quit()
        