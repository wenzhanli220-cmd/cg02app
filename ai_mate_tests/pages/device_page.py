from ai_mate_tests.pages.base_page import BasePage


class DevicePage(BasePage):
    def search_device(self):
        """搜索设备"""
        self.click_by_config("device_item")

    def pair_device(self):
        """配对设备"""
        self.click_by_config("pair_button")

    def is_paired_success(self, timeout=20):
        """检查配对成功"""
        try:
            elements = self.element_manager.get_success_elements(self.driver)
            return bool(elements)
        except Exception:
            return False

    def complete_pairing_flow(self):
        """完整配对流程"""
        self.search_device()
        self.pair_device()
        return self.is_paired_success()