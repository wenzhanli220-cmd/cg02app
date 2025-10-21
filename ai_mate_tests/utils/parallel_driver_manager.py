from appium import webdriver
from typing import Dict, List
import threading
from ai_mate_tests.utils.driver_factory import DriverFactory
from ai_mate_tests.utils.element_manager import ElementManager


class ParallelDriverManager:
    def __init__(self):
        self.driver_factory = DriverFactory()
        self.drivers: Dict[str, webdriver.Remote] = {}
        self.lock = threading.Lock()

    def create_driver(self, device_name: str, app_name: str = "ai_mate"):
        """创建驱动"""
        with self.lock:
            if device_name in self.drivers:
                self.quit_driver(device_name)

            driver = self.driver_factory.get_driver(device_name, app_name)
            driver.element_manager = ElementManager(driver.config_loader, device_name)
            self.drivers[device_name] = driver
            return driver

    def get_driver(self, device_name: str):
        """获取驱动"""
        with self.lock:
            return self.drivers[device_name]

    def quit_driver(self, device_name: str):
        """退出驱动"""
        with self.lock:
            if device_name in self.drivers:
                try:
                    self.drivers[device_name].quit()
                except Exception:
                    pass
                del self.drivers[device_name]

    def quit_all_drivers(self):
        """退出所有驱动"""
        with self.lock:
            for device_name in list(self.drivers.keys()):
                self.quit_driver(device_name)

    def get_available_devices(self) -> List[str]:
        """获取可用设备"""
        return self.driver_factory.config_loader.get_all_devices()


# 全局实例
parallel_driver_manager = ParallelDriverManager()