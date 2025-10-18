# pages/home_page.py
from ai_mate_tests.pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    def go_to_add_device(self):
        """点击首页的添加设备"""
        try:
            self.click_by_config("add_device")
            print(f"设备 {self.device_name}: 已点击添加设备")
        except Exception as e:
            print(f"设备 {self.device_name}: 点击添加设备失败: {e}")
            raise