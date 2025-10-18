# pages/popup_page.py
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from ai_mate_tests.pages.base_page import BasePage


class PopupPage(BasePage):
    """通用干扰弹窗处理（保留坐标点击备选方案）"""

    def __init__(self, driver):
        super().__init__(driver)
        # 保持原来的等待时长默认值，但我们允许通过参数覆盖
        self.wait = WebDriverWait(driver, 10)

    def handle_interference_popup(self, timeout: float = 3) -> bool:
        """
        检测并关闭干扰弹窗（兼容原有坐标点击）
        :param timeout: 等待弹窗出现的最大时间（秒），默认 3 秒（向后兼容）
        :return: 如果检测到并关闭弹窗则返回 True，否则返回 False
        """
        try:
            # 尝试根据元素定位弹窗（等待 timeout 秒）
            element = self.find_element_by_config("popup_button", timeout)

            if element:
                # 获取配置中的坐标
                coords = self.element_manager.config_loader.get_popup_close_coords(self.device_name)

                if coords:
                    print(f"设备 {self.device_name}: 检测到干扰弹窗，使用坐标点击 ({coords['x']}, {coords['y']}) 关闭")
                    try:
                        action = TouchAction(self.driver)
                        action.tap(x=coords['x'], y=coords['y']).perform()
                    except Exception as e:
                        # 如果坐标点击也失败，尽量尝试元素本身的 click() 方法作为回退
                        try:
                            element.click()
                        except Exception:
                            print(f"设备 {self.device_name}: 坐标点击和 element.click() 均失败: {e}")
                else:
                    # 如果没有配置坐标，直接点击元素
                    element.click()
                    print(f"设备 {self.device_name}: 检测到干扰弹窗，已点击关闭")

                return True

        except (TimeoutException, NoSuchElementException):
            # 没有弹窗，快速返回 False
            return False
        except Exception as e:
            print(f"设备 {self.device_name}: 处理干扰弹窗时发生异常: {e}")
            return False

        return False

    def is_popup_displayed(self, timeout=2):
        """检查是否显示弹窗"""
        try:
            return self.is_displayed_by_config("popup_button")
        except Exception as e:
            print(f"设备 {self.device_name}: 检查弹窗显示状态失败: {e}")
            return False