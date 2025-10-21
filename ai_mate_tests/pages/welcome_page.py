from ai_mate_tests.pages.base_page import BasePage

class WelcomePage(BasePage):
    def accept_all(self):
        """完成欢迎流程"""
        self.click_by_config("agree_protocol")
        self.click_by_config("use_now") 
        self.click_by_config("allow")