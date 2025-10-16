from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class PopupPage:
    """通用干扰弹窗处理（保留坐标点击备选方案）"""

    # 你原来的弹窗定位（示例）
    POPUP_BUTTON = (AppiumBy.CLASS_NAME, "android.widget.Button")

    def __init__(self, driver):
        self.driver = driver
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
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.POPUP_BUTTON)
            )

            # 如果找到了元素，按你原来的做法使用坐标点击（保证兼容）
            print("⚠️ 检测到干扰弹窗元素，使用坐标点击尝试关闭 (951, 1012)")
            try:
                action = TouchAction(self.driver)
                action.tap(x=951, y=1012).perform()
            except Exception as e:
                # 如果坐标点击也失败，尽量尝试元素本身的 click() 方法作为回退
                try:
                    element.click()
                except Exception:
                    print(f"⚠️ 坐标点击和 element.click() 均失败: {e}")

            return True

        except (TimeoutException, NoSuchElementException):
            # 没有弹窗，快速返回 False
            return False
