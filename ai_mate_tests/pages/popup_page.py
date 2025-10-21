from appium.webdriver.common.touch_action import TouchAction
from ai_mate_tests.pages.base_page import BasePage

class PopupPage(BasePage):
    def handle_interference_popup(self, timeout=2):
        """快速弹窗处理"""
        try:
            element = self.find_element_by_config("popup_button", timeout)
            if element:
                coords = self.element_manager.config_loader.get_popup_close_coords(self.device_name)
                if coords:
                    TouchAction(self.driver).tap(x=coords['x'], y=coords['y']).perform()
                else:
                    element.click()
                return True
        except Exception:
            return False