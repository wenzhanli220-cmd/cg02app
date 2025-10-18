# utils/element_manager.py
from typing import List
from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from ai_mate_tests.utils.config_loader import ConfigLoader


class ElementManager:
    def __init__(self, config_loader: ConfigLoader, device_name: str):
        self.config_loader = config_loader
        self.device_name = device_name

    # 实例方法 - 需要使用实例属性
    def click(self, driver: WebDriver, element_key: str) -> None:
        """点击元素 - 对应BasePage的click方法"""
        by, locator = self._get_locator(element_key)
        driver.find_element(by, locator).click()

    # 静态方法 - 不依赖实例状态
    @staticmethod
    def click_by_xpath(driver: WebDriver, xpath: str) -> None:
        """通过xpath点击 - 对应BasePage的click_by_xpath方法"""
        driver.find_element(AppiumBy.XPATH, xpath).click()

    @staticmethod
    def click_by_accessibility_id(driver: WebDriver, acc_id: str) -> None:
        """通过accessibility_id点击 - 对应BasePage的click_by_accessibility_id方法"""
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, acc_id).click()

    @staticmethod
    def click_by_text(driver: WebDriver, text: str) -> None:
        """通过文本点击 - 对应BasePage的click_by_text方法"""
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")').click()

    @staticmethod
    def tap_coordinate(driver: WebDriver, x: int, y: int) -> None:
        """点击坐标"""
        driver.tap([(x, y)])

    # 实例方法 - 需要使用实例属性
    def is_displayed(self, driver: WebDriver, element_key: str) -> bool:
        """检查元素是否显示 - 对应BasePage的is_displayed方法"""
        try:
            by, locator = self._get_locator(element_key)
            return driver.find_element(by, locator).is_displayed()
        except Exception:
            return False

    def find_element(self, driver: WebDriver, element_key: str, timeout: int = 5) -> WebElement:
        """
        支持显式等待的find_element - 对应BasePage的find_element方法

        :param driver: WebDriver实例
        :param element_key: 元素键名
        :param timeout: 等待时间（秒）
        :return: 找到的WebElement
        """
        by, locator = self._get_locator(element_key)
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )

    def find_elements(self, driver: WebDriver, element_key: str, timeout: int = 5) -> List[WebElement]:
        """
        查找多个元素

        :param driver: WebDriver实例
        :param element_key: 元素键名
        :param timeout: 等待时间（秒）
        :return: 找到的WebElement列表
        """
        by, locator = self._get_locator(element_key)
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, locator))
        )

    def input_text(self, driver: WebDriver, element_key: str, text: str) -> None:
        """输入文本"""
        element = self.find_element(driver, element_key)
        element.clear()
        element.send_keys(text)

    def get_text(self, driver: WebDriver, element_key: str) -> str:
        """获取元素文本"""
        element = self.find_element(driver, element_key)
        return element.text

    def _get_locator(self, element_key: str) -> tuple[str, str]:
        """内部方法：获取定位器"""
        locator_config = self.config_loader.get_element_locator(self.device_name, element_key)
        result = ConfigLoader.convert_locator_to_appium_format(locator_config)
        # 类型安全转换
        if isinstance(result, tuple) and len(result) == 2:
            return result[0], result[1]
        elif isinstance(result, list) and len(result) == 2:
            return result[0], result[1]
        else:
            raise ValueError(f"Invalid locator format: {result}")

    def _get_locator_by_page(self, page: str, element_key: str) -> tuple[str, str]:
        """内部方法：按页面获取定位器"""
        locator_config = self.config_loader.get_element_by_page(self.device_name, page, element_key)
        result = ConfigLoader.convert_locator_to_appium_format(locator_config)
        # 类型安全转换
        if isinstance(result, tuple) and len(result) == 2:
            return result[0], result[1]
        elif isinstance(result, list) and len(result) == 2:
            return result[0], result[1]
        else:
            raise ValueError(f"Invalid locator format: {result}")

    def get_success_elements(self, driver: WebDriver) -> List[WebElement]:
        """获取所有成功验证元素"""
        success_texts = self.config_loader.get_success_texts(self.device_name)
        found_elements = []

        for text_config in success_texts:
            try:
                by, value = ConfigLoader.convert_locator_to_appium_format(text_config)
                element = driver.find_element(by, value)
                if element:
                    found_elements.append(element)
            except Exception:
                continue

        return found_elements

    def close_popup_by_coords(self, driver: WebDriver) -> bool:
        """通过坐标关闭弹窗"""
        coords = self.config_loader.get_popup_close_coords(self.device_name)
        if coords:
            self.tap_coordinate(driver, coords['x'], coords['y'])
            return True
        return False