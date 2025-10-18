# pages/base_page.py
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.device_name = getattr(driver, 'device_name', 'device1')

        # 延迟初始化element_manager
        self._element_manager = None

    @property
    def element_manager(self):
        """延迟初始化element_manager"""
        if self._element_manager is None:
            # 如果driver已经有element_manager，直接使用
            if hasattr(self.driver, 'element_manager'):
                self._element_manager = self.driver.element_manager
            else:
                # 单设备测试时，动态导入并初始化
                try:
                    from ai_mate_tests.utils.config_loader import ConfigLoader
                    from ai_mate_tests.utils.element_manager import ElementManager
                    config_loader = ConfigLoader()
                    self._element_manager = ElementManager(config_loader, self.device_name)
                except Exception as e:
                    print(f"⚠️ element_manager初始化失败: {e}")
                    print("💡 提示: 请确保config.yaml文件位于正确位置")
                    self._element_manager = None
        return self._element_manager

    # ... 其余方法保持不变 ...

    # ========== 配置分离的核心方法 ==========

    def click_by_config(self, element_key):
        """通过配置键名点击元素"""
        if self.element_manager:
            return self.element_manager.click(self.driver, element_key)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def is_displayed_by_config(self, element_key):
        """通过配置键名检查元素是否显示"""
        if self.element_manager:
            return self.element_manager.is_displayed(self.driver, element_key)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def find_element_by_config(self, element_key, timeout=5):
        """通过配置键名查找元素"""
        if self.element_manager:
            return self.element_manager.find_element(self.driver, element_key, timeout)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def find_elements_by_config(self, element_key, timeout=5):
        """通过配置键名查找多个元素"""
        if self.element_manager:
            return self.element_manager.find_elements(self.driver, element_key, timeout)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def input_text_by_config(self, element_key, text):
        """通过配置键名输入文本"""
        if self.element_manager:
            return self.element_manager.input_text(self.driver, element_key, text)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def get_text_by_config(self, element_key):
        """通过配置键名获取元素文本"""
        if self.element_manager:
            return self.element_manager.get_text(self.driver, element_key)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    def wait_for_element_by_config(self, element_key, timeout=10):
        """等待配置元素可见"""
        if self.element_manager:
            return self.element_manager.wait_for_element_visible(self.driver, element_key, timeout)
        else:
            raise RuntimeError("element_manager未初始化，无法使用配置分离功能")

    # ========== 保留原有直接定位方法 ==========

    def click(self, by, locator):
        """直接通过定位方式点击元素"""
        self.driver.find_element(by, locator).click()

    def click_by_xpath(self, xpath):
        """通过xpath点击元素"""
        self.click(AppiumBy.XPATH, xpath)

    def click_by_accessibility_id(self, acc_id):
        """通过accessibility_id点击元素"""
        self.click(AppiumBy.ACCESSIBILITY_ID, acc_id)

    def click_by_text(self, text):
        """通过文本点击元素"""
        self.click(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    def is_displayed(self, by, locator):
        """检查元素是否显示"""
        try:
            return self.driver.find_element(by, locator).is_displayed()
        except:
            return False

    def find_element(self, by, locator, timeout=5):
        """
        支持显式等待的 find_element
        :param by: 定位方式
        :param locator: 定位值
        :param timeout: 等待时间（秒）
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )

    def find_elements(self, by, locator, timeout=5):
        """查找多个元素"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, locator))
        )

    def wait_for_element(self, by, locator, timeout=10):
        """等待元素可见"""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, locator))
        )

    def input_text(self, by, locator, text):
        """输入文本"""
        element = self.find_element(by, locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, by, locator):
        """获取元素文本"""
        element = self.find_element(by, locator)
        return element.text

    # ========== 通用工具方法 ==========

    def take_screenshot(self):
        """截图"""
        screenshot = self.driver.get_screenshot_as_png()
        # 可以在这里添加截图保存或附件的逻辑
        return screenshot

    def get_page_source(self):
        """获取页面源码"""
        return self.driver.page_source

    def swipe(self, start_x, start_y, end_x, end_y, duration=800):
        """滑动操作"""
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    def back(self):
        """返回操作"""
        self.driver.back()

    def get_current_activity(self):
        """获取当前activity"""
        return self.driver.current_activity

    def get_current_package(self):
        """获取当前包名"""
        return self.driver.current_package