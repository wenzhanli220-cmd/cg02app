# pages/device_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from ai_mate_tests.pages.base_page import BasePage


class DevicePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    def search_device(self):
        """搜索设备"""
        try:
            self.click_by_config("device_item")
            print(f"设备 {self.device_name}: 已选择设备")
        except Exception as e:
            print(f"设备 {self.device_name}: 搜索设备失败: {e}")
            raise

    def pair_device(self):
        """配对设备"""
        try:
            self.click_by_config("pair_button")
            print(f"设备 {self.device_name}: 已点击配对")
        except Exception as e:
            print(f"设备 {self.device_name}: 配对设备失败: {e}")
            raise

    def is_paired_success(self, timeout=10):
        """等待配对成功"""
        try:
            success_elements = self.element_manager.get_success_elements(self.driver)
            if success_elements:
                print(f"设备 {self.device_name}: 配对成功")
                return True
            else:
                print(f"设备 {self.device_name}: 未找到成功验证元素")
                return False
        except Exception as e:
            print(f"设备 {self.device_name}: 检查配对状态失败: {e}")
            return False

    def wait_for_pairing_success(self, timeout=15):
        """等待配对成功（带超时）"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: len(self.element_manager.get_success_elements(driver)) > 0
            )
            print(f"设备 {self.device_name}: 配对成功验证完成")
            return True
        except TimeoutException:
            print(f"设备 {self.device_name}: 配对成功验证超时")
            return False

    def complete_pairing_flow(self):
        """完整的配对流程"""
        try:
            self.search_device()
            self.pair_device()
            return self.wait_for_pairing_success()
        except Exception as e:
            print(f"设备 {self.device_name}: 完整配对流程失败: {e}")
            return False

    def is_device_list_loaded(self):
        """检查设备列表是否加载完成"""
        try:
            return self.is_displayed_by_config("device_item")
        except Exception as e:
            print(f"设备 {self.device_name}: 检查设备列表加载状态失败: {e}")
            return False

    def wait_for_device_list(self, timeout=10):
        """等待设备列表加载完成"""
        try:
            self.wait_for_element_by_config("device_item", timeout)
            print(f"设备 {self.device_name}: 设备列表加载完成")
            return True
        except Exception as e:
            print(f"设备 {self.device_name}: 设备列表加载失败: {e}")
            return False