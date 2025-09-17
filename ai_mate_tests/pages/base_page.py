from appium.webdriver.common.appiumby import AppiumBy

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def click(self, by, locator):
        self.driver.find_element(by, locator).click()

    def click_by_xpath(self, xpath):
        self.click(AppiumBy.XPATH, xpath)

    def click_by_accessibility_id(self, acc_id):
        self.click(AppiumBy.ACCESSIBILITY_ID, acc_id)

    def click_by_text(self, text):
        self.click(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    def is_displayed(self, by, locator):
        try:
            return self.driver.find_element(by, locator).is_displayed()
        except:
            return False
