from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage

class HomePage(BasePage):

    ADD_DEVICE = (AppiumBy.ACCESSIBILITY_ID, "添加设备")

    def go_to_add_device(self):
        """点击首页的添加设备（暂时没用到，可扩展）"""
        self.click(*self.ADD_DEVICE)
