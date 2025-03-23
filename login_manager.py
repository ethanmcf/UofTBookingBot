class LoginManager():
    def __init__(self, login_file_path, code_file_path):
        self.login_file_path = login_file_path
        self.code_file_path = code_file_path
        self.quit = lambda: exit(1)

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

    def get_code(self):
        try:
            with open(self.code_file_path, 'r') as file:
                code = file.readline().strip()
                if not code:
                    raise Exception("Missing code in the bypass code file")
                
                self._remove_code(code)
                return code
        except:
            print("Error with bypass code file")
            self.quit()

    def _remove_code(self, code):
        try:
            with open(self.code_file_path, 'r') as file:
                lines = file.readlines()  

            with open(self.code_file_path, "w") as file:
                for line in lines:
                    if line.strip("\n") != code.strip("\n"): 
                        file.write(line) 
        except:
            print("Error writing to bypass code file")
            self.quit()

    def num_codes_left(self):
        try:
            with open(self.code_file_path, 'r') as file:
                return sum(1 for _ in file) 
        except:
            print("Error reading to bypass code file")
            self.quit()

    def save_codes(self, codes):        
        try:
            with open(self.code_file_path, 'w') as file:
                for code in codes:
                    file.write(code + '\n')
        except:
            print("Error writing to bypass code file")
            self.quit()
