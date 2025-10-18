# utils/parallel_driver_manager.py
from appium import webdriver


from typing import Dict, List, Optional
import threading
import logging
from datetime import datetime

from ai_mate_tests.utils.driver_factory import DriverFactory
from ai_mate_tests.utils.element_manager import ElementManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParallelDriverManager:
    def __init__(self):
        self.driver_factory = DriverFactory()
        self.drivers: Dict[str, webdriver.Remote] = {}
        self.lock = threading.Lock()
        self._test_context = {}  # 存储测试上下文信息

    def create_driver(self, device_name: str, app_name: str = "ai_mate") -> webdriver.Remote:
        """创建并管理driver"""
        with self.lock:
            # 检查是否已存在该设备的driver
            if device_name in self.drivers:
                logger.warning(f"设备 {device_name} 的driver已存在，正在重新创建...")
                self.quit_driver(device_name)

            # 创建新driver
            driver = self.driver_factory.get_driver(device_name, app_name)

            # 初始化元素管理器
            driver.element_manager = ElementManager(driver.config_loader, device_name)

            # 存储driver
            self.drivers[device_name] = driver

            # 初始化测试上下文
            self._test_context[device_name] = {
                'test_status': 'running',
                'start_time': None,
                'current_test': None
            }

            logger.info(f"✅ 并行管理器: 设备 {device_name} 的driver创建完成")
            return driver

    def get_driver(self, device_name: str) -> webdriver.Remote:
        """获取已创建的driver"""
        with self.lock:
            if device_name not in self.drivers:
                raise ValueError(f"设备 {device_name} 的driver尚未创建")
            return self.drivers[device_name]

    def get_all_drivers(self) -> Dict[str, webdriver.Remote]:
        """获取所有已创建的drivers"""
        with self.lock:
            return self.drivers.copy()

    def switch_application(self, device_name: str, new_app_name: str) -> webdriver.Remote:
        """切换指定设备的应用"""
        with self.lock:
            if device_name not in self.drivers:
                raise ValueError(f"设备 {device_name} 的driver尚未创建")

            driver = self.driver_factory.switch_application(
                self.drivers[device_name],
                new_app_name
            )

            # 更新driver引用
            self.drivers[device_name] = driver

            # 重新初始化元素管理器
            driver.element_manager = ElementManager(driver.config_loader, device_name)

            logger.info(f"设备 {device_name}: 已切换到应用 {new_app_name}")
            return driver

    def restart_driver(self, device_name: str, app_name: str = None) -> webdriver.Remote:
        """重启指定设备的driver"""
        with self.lock:
            if device_name in self.drivers:
                try:
                    self.drivers[device_name].quit()
                except Exception as e:
                    logger.warning(f"重启设备 {device_name} 时退出旧driver出错: {e}")
                finally:
                    del self.drivers[device_name]

            # 创建新driver
            return self.create_driver(device_name, app_name)

    def quit_driver(self, device_name: str):
        """退出指定设备的driver"""
        with self.lock:
            if device_name in self.drivers:
                try:
                    self.drivers[device_name].quit()
                    logger.info(f"✅ 已退出设备 {device_name} 的driver")
                except Exception as e:
                    logger.error(f"❌ 退出设备 {device_name} 的driver时出错: {e}")
                finally:
                    del self.drivers[device_name]

                # 清理测试上下文
                if device_name in self._test_context:
                    del self._test_context[device_name]

    def quit_all_drivers(self):
        """退出所有driver"""
        with self.lock:
            logger.info("正在退出所有并行管理的driver...")
            for device_name in list(self.drivers.keys()):
                self.quit_driver(device_name)

            # 清理所有上下文
            self._test_context.clear()
            logger.info("✅ 所有并行管理的driver退出完成")

    def get_available_devices(self) -> List[str]:
        """获取所有可用设备名称"""
        return self.driver_factory.config_loader.get_all_devices()

    def get_active_devices(self) -> List[str]:
        """获取当前活跃的设备列表"""
        with self.lock:
            return list(self.drivers.keys())

    def get_driver_status(self, device_name: str) -> Optional[Dict]:
        """获取driver状态信息"""
        with self.lock:
            if device_name not in self.drivers:
                return None

            driver = self.drivers[device_name]
            try:
                return {
                    'device_name': device_name,
                    'app_name': getattr(driver, 'app_name', 'unknown'),
                    'server_url': getattr(driver, 'server_url', 'unknown'),
                    'session_id': driver.session_id,
                    'capabilities': driver.capabilities,
                    'test_context': self._test_context.get(device_name, {})
                }
            except Exception as e:
                logger.warning(f"获取设备 {device_name} 状态时出错: {e}")
                return {
                    'device_name': device_name,
                    'status': 'error',
                    'error': str(e)
                }

    def get_all_drivers_status(self) -> Dict[str, Dict]:
        """获取所有drivers的状态信息"""
        with self.lock:
            status = {}
            for device_name in self.drivers.keys():
                status[device_name] = self.get_driver_status(device_name)
            return status

    def set_test_context(self, device_name: str, key: str, value: any):
        """设置测试上下文信息"""
        with self.lock:
            if device_name not in self._test_context:
                self._test_context[device_name] = {}
            self._test_context[device_name][key] = value

    def get_test_context(self, device_name: str, key: str, default=None):
        """获取测试上下文信息"""
        with self.lock:
            device_context = self._test_context.get(device_name, {})
            return device_context.get(key, default)

    def start_test(self, device_name: str, test_name: str):
        """标记测试开始"""
        self.set_test_context(device_name, 'current_test', test_name)
        self.set_test_context(device_name, 'test_status', 'running')
        self.set_test_context(device_name, 'start_time', self._get_current_time())
        logger.info(f"设备 {device_name}: 开始测试 {test_name}")

    def end_test(self, device_name: str, status: str = 'completed'):
        """标记测试结束"""
        self.set_test_context(device_name, 'test_status', status)
        self.set_test_context(device_name, 'end_time', self._get_current_time())
        logger.info(f"设备 {device_name}: 测试结束，状态: {status}")

    def _get_current_time(self):
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def execute_on_all_drivers(self, func, *args, **kwargs):
        """
        在所有活跃的drivers上执行函数
        :param func: 要执行的函数，第一个参数必须是driver
        """
        results = {}
        with self.lock:
            for device_name, driver in self.drivers.items():
                try:
                    result = func(driver, *args, **kwargs)
                    results[device_name] = {'status': 'success', 'result': result}
                except Exception as e:
                    results[device_name] = {'status': 'error', 'error': str(e)}
                    logger.error(f"在设备 {device_name} 上执行函数时出错: {e}")

        return results


# 创建全局实例
parallel_driver_manager = ParallelDriverManager()


# 便捷函数
def create_driver(device_name: str, app_name: str = "ai_mate"):
    """创建driver (便捷函数)"""
    return parallel_driver_manager.create_driver(device_name, app_name)


def get_driver(device_name: str):
    """获取driver (便捷函数)"""
    return parallel_driver_manager.get_driver(device_name)


def quit_all_drivers():
    """退出所有driver (便捷函数)"""
    parallel_driver_manager.quit_all_drivers()


def get_drivers_status():
    """获取所有drivers状态 (便捷函数)"""
    return parallel_driver_manager.get_all_drivers_status()