# pages/welcome_page.py
from ai_mate_tests.pages.base_page import BasePage


class WelcomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    def accept_all(self):
        """依次点击：同意协议 -> 立即使用 -> 允许权限"""
        try:
            self.click_by_config("agree_protocol")
            self.click_by_config("use_now")
            self.click_by_config("allow")
            print(f"设备 {self.device_name}: 欢迎流程完成")
        except Exception as e:
            print(f"设备 {self.device_name}: 欢迎流程执行失败: {e}")
            raise

    def is_welcome_complete(self):
        """检查欢迎流程是否完成"""
        try:
            # 检查是否还能找到欢迎页的元素，如果找不到说明已经进入首页
            return not self.is_displayed_by_config("agree_protocol")
        except Exception as e:
            print(f"设备 {self.device_name}: 检查欢迎流程完成状态失败: {e}")
            return False

    def wait_for_welcome_page(self, timeout=10):
        """等待欢迎页面加载完成"""
        try:
            self.find_element_by_config("agree_protocol", timeout)
            print(f"设备 {self.device_name}: 欢迎页面加载完成")
            return True
        except Exception as e:
            print(f"设备 {self.device_name}: 欢迎页面加载失败: {e}")
            return False

    def handle_permission_popups(self):
        """处理可能的权限弹窗"""
        try:
            # 尝试处理可能的权限弹窗
            if self.is_displayed_by_config("allow"):
                self.click_by_config("allow")
                print(f"设备 {self.device_name}: 已处理权限弹窗")
            return True
        except Exception:
            # 如果没有权限弹窗，正常继续
            return True