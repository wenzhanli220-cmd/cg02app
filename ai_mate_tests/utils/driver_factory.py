# utils/driver_factory.py
from appium import webdriver
from appium.options.android import UiAutomator2Options

import logging

from ai_mate_tests.utils.config_loader import ConfigLoader

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriverFactory:
    def __init__(self):
        self.config_loader = ConfigLoader()
        self._created_drivers = {}  # 跟踪已创建的drivers

    def get_driver(self, device_name: str, app_name: str = "ai_mate"):
        """
        获取指定设备的driver
        :param device_name: 设备名称，如 "device1", "device2"
        :param app_name: 应用名称，"ai_mate" 或 "settings"
        """
        # 验证设备配置
        if not self.config_loader.validate_device_config(device_name):
            raise ValueError(f"设备 {device_name} 配置验证失败")

        # 获取设备配置
        device_config = self.config_loader.get_device_capabilities(device_name)
        appium_server_url = self.config_loader.get_appium_server_url(device_name)

        # 创建Options对象
        options = UiAutomator2Options()

        # 基础设备配置
        options.platform_name = device_config["platformName"]
        options.platform_version = device_config["platformVersion"]
        options.device_name = device_config["deviceName"]
        options.automation_name = device_config["automationName"]
        options.udid = device_config["udid"]

        # 应用配置
        app_config = self.config_loader.get_app_config(app_name)
        if not app_config:
            raise ValueError(f"应用配置 {app_name} 不存在")

        options.app_package = app_config["appPackage"]
        options.app_activity = app_config["appActivity"]

        # 超时配置
        options.uiautomator2_server_launch_timeout = device_config.get(
            "uiautomator2_server_launch_timeout", 60000
        )
        options.uiautomator2_server_install_timeout = device_config.get(
            "uiautomator2_server_install_timeout", 60000
        )
        options.app_wait_activity = device_config.get("app_wait_activity", "")
        options.app_wait_duration = device_config.get("app_wait_duration", 60000)

        # 其他驱动选项
        driver_options = self.config_loader.get_driver_options()
        for key, value in driver_options.items():
            try:
                setattr(options, key, value)
            except AttributeError as e:
                logger.warning(f"无法设置驱动选项 {key}: {e}")

        logger.info(f"创建driver - 设备: {device_name}, 应用: {app_name}, 服务器: {appium_server_url}")
        logger.info(f"设备UDID: {device_config['udid']}, 应用包名: {app_config['appPackage']}")

        try:
            # 创建driver
            driver = webdriver.Remote(
                command_executor=appium_server_url,
                options=options
            )

            # 设置隐式等待
            driver.implicitly_wait(10)

            # 保存设备信息
            driver.device_name = device_name
            driver.app_name = app_name
            driver.config_loader = self.config_loader
            driver.server_url = appium_server_url

            # 记录创建的driver
            self._created_drivers[device_name] = {
                'driver': driver,
                'app_name': app_name,
                'server_url': appium_server_url
            }

            logger.info(f"✅ 成功创建设备 {device_name} 的driver")
            return driver

        except Exception as e:
            logger.error(f"❌ 创建设备 {device_name} 的driver失败: {e}")
            raise

    def switch_application(self, driver, new_app_name: str):
        """
        切换应用
        :param driver: 现有的driver实例
        :param new_app_name: 新的应用名称
        """
        device_name = getattr(driver, 'device_name', 'unknown')
        logger.info(f"设备 {device_name}: 切换应用到 {new_app_name}")

        try:
            # 先退出当前driver
            driver.quit()

            # 重新创建driver
            new_driver = self.get_driver(device_name, new_app_name)
            return new_driver

        except Exception as e:
            logger.error(f"设备 {device_name}: 切换应用到 {new_app_name} 失败: {e}")
            raise

    def restart_driver(self, device_name: str, app_name: str = None):
        """
        重启指定设备的driver
        """
        if device_name in self._created_drivers:
            try:
                old_driver = self._created_drivers[device_name]['driver']
                old_driver.quit()
                logger.info(f"已退出设备 {device_name} 的旧driver")
            except Exception as e:
                logger.warning(f"退出设备 {device_name} 的旧driver时出错: {e}")
            finally:
                del self._created_drivers[device_name]

        # 获取原来的应用名称或使用新的
        if app_name is None and device_name in self._created_drivers:
            app_name = self._created_drivers[device_name]['app_name']
        elif app_name is None:
            app_name = "ai_mate"

        return self.get_driver(device_name, app_name)

    def get_created_drivers_info(self):
        """获取已创建drivers的信息"""
        return {
            device: {
                'app_name': info['app_name'],
                'server_url': info['server_url'],
                'session_id': info['driver'].session_id if info['driver'] else None
            }
            for device, info in self._created_drivers.items()
        }

    def quit_all_drivers(self):
        """退出所有已创建的drivers"""
        logger.info("正在退出所有driver...")
        for device_name, info in list(self._created_drivers.items()):
            try:
                if info['driver']:
                    info['driver'].quit()
                    logger.info(f"✅ 已退出设备 {device_name} 的driver")
            except Exception as e:
                logger.error(f"❌ 退出设备 {device_name} 的driver时出错: {e}")
            finally:
                del self._created_drivers[device_name]

        logger.info("所有driver退出完成")


# 创建全局实例
driver_factory = DriverFactory()


# 兼容原有接口的函数
def get_driver(device_name="device1", app_name="ai_mate"):
    """
    获取driver (兼容原有接口)
    :param device_name: 设备名称，默认为 "device1"
    :param app_name: 应用名称，"ai_mate" 或 "settings"
    """
    return driver_factory.get_driver(device_name, app_name)


def switch_app(driver, new_app_name: str):
    """
    切换应用 (便捷函数)
    """
    return driver_factory.switch_application(driver, new_app_name)


def restart_driver(device_name: str, app_name: str = None):
    """
    重启driver (便捷函数)
    """
    return driver_factory.restart_driver(device_name, app_name)