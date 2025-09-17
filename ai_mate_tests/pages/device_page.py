from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ai_mate_tests.pages.base_page import BasePage



class DevicePage(BasePage):

    DEVICE_ITEM = (AppiumBy.XPATH, '//android.widget.ImageView[@content-desc="Infinix AI Glasses"]')
    PAIR_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@resource-id="com.transsion.settings.bluetooth:id/btn_positive"]')
    DIALOG_TRANSLATE_TEXT = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("对话翻译")')

    def search_device(self):
        self.click(*self.DEVICE_ITEM)

    def pair_device(self):
        self.click(*self.PAIR_BUTTON)

    def is_paired_success(self, timeout=10):
        """
        等待 '对话翻译' 文本出现，表示配对成功并跳转页面
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.DIALOG_TRANSLATE_TEXT)
            )
            return True
        except:
            return False
