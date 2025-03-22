from Pages.BasePage import BasePage

class CodePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.get_codes_btn = ()
        self.codes_txt = ()
    
    def generate_codes(self):
        pass
