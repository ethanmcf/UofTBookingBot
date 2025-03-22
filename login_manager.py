class LoginManager():
    def __init__(self, login_file_path, code_file_path, codes_page):
        self.login_file_path = login_file_path
        self.code_file_path = code_file_path
        self.codes_page = codes_page

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
                    self._reload_codes()
                return code
        except:
            print("Error with bypass code file")
            self.quit()

    def _reload_codes(self):
        codes = self.codes_page.generate_codes()
        self._write_codes(codes)


    def _write_codes(self, codes):        
        try:
            with open(self.code_file_path, 'w') as file:
                for code in codes:
                    file.write(code + '\n')
        except:
            print("Error writing to bypass code file")
            self.quit()