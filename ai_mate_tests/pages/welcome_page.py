from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException

from ai_mate_tests.pages.base_page import BasePage


class WelcomePage(BasePage):

    AGREE_PROTOCOL = (
        AppiumBy.XPATH,
        '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[2]'
    )
    USE_NOW = (AppiumBy.ACCESSIBILITY_ID, "立即使用")
    ALLOW = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("允许")')

    def accept_all(self):
        """依次点击：同意协议 -> 立即使用 -> 允许权限"""
        self.click(*self.AGREE_PROTOCOL)
        self.click(*self.USE_NOW)
        self.click(*self.ALLOW)



