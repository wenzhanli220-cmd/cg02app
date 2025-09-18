from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from ai_mate_tests.pages.base_page import BasePage


class DevicePage(BasePage):

    DEVICE_ITEM = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Infinix AI Glasses"]')
    PAIR_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@resource-id="com.transsion.settings.bluetooth:id/btn_positive"]')
    SUCCESS_TEXTS = [
        (AppiumBy.ACCESSIBILITY_ID, "对话翻译"),
        (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="对话翻译"]')
    ]

    def search_device(self):
        self.click(*self.DEVICE_ITEM)

    def pair_device(self):
        self.click(*self.PAIR_BUTTON)

    def is_paired_success(self, timeout=10):
        """等待首页出现 '对话翻译' 或 '现场听译'"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: any(d.find_elements(*locator) for locator in self.SUCCESS_TEXTS)
            )
            return True
        except TimeoutException:
            return False
