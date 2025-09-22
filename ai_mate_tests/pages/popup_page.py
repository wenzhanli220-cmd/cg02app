from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from ai_mate_tests.pages.base_page import BasePage


class PopupPage(BasePage):
    """
    干扰弹窗页面处理
    """

    POPUP_BUTTON = (AppiumBy.XPATH, "//android.widget.Button[@text='开始连接']")

    def handle_interference_popup(self):
        """
        如果检测到干扰弹窗，则点击指定坐标 (951, 1012)，否则跳过
        """
        try:
            popup_button = self.find_element(*self.POPUP_BUTTON, timeout=2)
            if popup_button:
                print("⚠️ 检测到干扰弹窗，点击坐标 (951, 1012) 关闭")
                action = TouchAction(self.driver)
                action.tap(x=951, y=1012).perform()
            else:
                print("✅ 未检测到干扰弹窗，继续执行")
        except (NoSuchElementException, TimeoutException):
            print("✅ 未检测到干扰弹窗，继续执行")
        except Exception as e:
            print(f"❌ 处理干扰弹窗时发生异常: {e}")
