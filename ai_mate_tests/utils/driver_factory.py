# utils/driver_factory.py
from appium import webdriver
from appium.options.android import UiAutomator2Options

import logging
import time
import subprocess

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

        options.app_package = app_config["app_package"]
        options.app_activity = app_config["app_activity"]

        # 针对不同应用的特定配置 - 主要修改点1：为AI Mate应用添加特殊配置
        if app_name == "settings":
            # 为设置应用添加特定配置
            options.auto_grant_permissions = True
            options.no_reset = True
            options.full_reset = False
            # 增加超时设置
            options.new_command_timeout = 300
            options.uiautomator2_server_launch_timeout = 120000
            options.uiautomator2_server_install_timeout = 120000
            options.app_wait_duration = 45000
            # 使用通配符匹配Activity
            options.app_wait_activity = "*.Settings,com.android.settings.*,com.transsion.*"
            # 禁用动画以确保稳定启动
            options.disable_window_animation = True
        elif app_name == "ai_mate":
            # AI Mate应用的特殊配置 - 主要修改点2：针对com.transsion.xsound优化
            options.auto_grant_permissions = True
            options.no_reset = True  # 系统应用使用no_reset
            options.full_reset = False
            # 增加超时设置
            options.new_command_timeout = 300
            options.uiautomator2_server_launch_timeout = 90000
            options.uiautomator2_server_install_timeout = 90000
            options.app_wait_duration = 30000
            # 使用通配符匹配Activity
            options.app_wait_activity = "com.transsion.xsound.*"
            # 性能优化
            options.skip_device_initialization = True
            options.disable_window_animation = True

        # 超时配置
        options.uiautomator2_server_launch_timeout = device_config.get(
            "uiautomator2ServerLaunchTimeout",
            options.uiautomator2_server_launch_timeout
        )
        options.uiautomator2_server_install_timeout = device_config.get(
            "uiautomator2ServerInstallTimeout",
            options.uiautomator2_server_install_timeout
        )

        # 其他驱动选项
        driver_options = self.config_loader.get_driver_options()
        for key, value in driver_options.items():
            try:
                camel_key = self._to_camel_case(key)
                setattr(options, camel_key, value)
            except AttributeError as e:
                logger.debug(f"无法设置驱动选项 {key}: {e}")

        # 对于传音设备的特殊处理
        if device_config["udid"] == "11467253AU000413":
            logger.debug("检测到传音设备，应用特殊配置...")
            # 增加更多启动选项
            options.disable_android_watchers = True
            options.skip_device_initialization = True
            options.skip_server_installation = True
            options.ignore_unimportant_views = True

        logger.info(f"创建 {device_name} 的 {app_name} 应用driver")

        try:
            # 主要修改点3：统一应用关闭逻辑，支持AI Mate应用
            if app_name in ["settings", "ai_mate"]:
                self._ensure_app_closed(device_config["udid"], app_config["app_package"])
                time.sleep(2)

            # 创建driver
            driver = webdriver.Remote(
                command_executor=appium_server_url,
                options=options
            )

            # 设置隐式等待
            driver.implicitly_wait(15)

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

            logger.info(f"✅ 成功创建 {device_name} 的 {app_name} 应用driver")
            return driver

        except Exception as e:
            logger.error(f"❌ 创建 {device_name} 的 {app_name} 应用driver失败: {e}")

            # 主要修改点4：统一调试逻辑，支持AI Mate应用
            self._debug_app_issue(device_config["udid"], app_config["app_package"], app_name)
            raise

    def _ensure_app_closed(self, udid, package_name):
        """确保应用已关闭 - 主要修改点5：统一应用关闭方法"""
        try:
            subprocess.run(
                f"adb -s {udid} shell am force-stop {package_name}",
                shell=True,
                capture_output=True
            )
            logger.debug(f"已强制停止 {package_name} 应用")
        except Exception as e:
            logger.debug(f"停止 {package_name} 应用时出错: {e}")

    def _debug_app_issue(self, udid, package_name, app_name):
        """调试应用启动问题 - 主要修改点6：统一调试方法"""
        logger.info(f"🔧 调试 {app_name} 应用启动问题...")

        try:
            # 检查当前Activity
            result = subprocess.run(
                f"adb -s {udid} shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'",
                shell=True,
                capture_output=True,
                text=True
            )
            logger.info(f"当前窗口焦点: {result.stdout}")

            # 检查应用进程
            result = subprocess.run(
                f"adb -s {udid} shell ps | grep {package_name}",
                shell=True,
                capture_output=True,
                text=True
            )
            logger.info(f"{app_name} 应用进程: {result.stdout}")

        except Exception as e:
            logger.debug(f"调试过程中出错: {e}")

    def _to_camel_case(self, snake_str):
        """将下划线命名法转换为驼峰命名法"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    # 以下方法保持不变
    def switch_application(self, driver, new_app_name: str):
        device_name = getattr(driver, 'device_name', 'unknown')
        logger.info(f"{device_name}: 切换应用到 {new_app_name}")

        try:
            driver.quit()
            new_driver = self.get_driver(device_name, new_app_name)
            return new_driver
        except Exception as e:
            logger.error(f"{device_name}: 切换应用到 {new_app_name} 失败: {e}")
            raise

    def restart_driver(self, device_name: str, app_name: str = None):
        if device_name in self._created_drivers:
            try:
                old_driver = self._created_drivers[device_name]['driver']
                old_driver.quit()
                logger.info(f"已退出 {device_name} 的旧driver")
            except Exception as e:
                logger.warning(f"退出 {device_name} 的旧driver时出错: {e}")
            finally:
                del self._created_drivers[device_name]

        if app_name is None and device_name in self._created_drivers:
            app_name = self._created_drivers[device_name]['app_name']
        elif app_name is None:
            app_name = "ai_mate"

        return self.get_driver(device_name, app_name)

    def get_created_drivers_info(self):
        return {
            device: {
                'app_name': info['app_name'],
                'server_url': info['server_url'],
                'session_id': info['driver'].session_id if info['driver'] else None
            }
            for device, info in self._created_drivers.items()
        }

    def quit_all_drivers(self):
        logger.info("正在退出所有driver...")
        for device_name, info in list(self._created_drivers.items()):
            try:
                if info['driver']:
                    info['driver'].quit()
                    logger.info(f"✅ 已退出 {device_name} 的driver")
            except Exception as e:
                logger.error(f"❌ 退出 {device_name} 的driver时出错: {e}")
            finally:
                del self._created_drivers[device_name]
        logger.info("所有driver退出完成")


# 创建全局实例
driver_factory = DriverFactory()


# 兼容原有接口的函数
def get_driver(device_name="device1", app_name="ai_mate"):
    return driver_factory.get_driver(device_name, app_name)


def switch_app(driver, new_app_name: str):
    return driver_factory.switch_application(driver, new_app_name)


def restart_driver(device_name: str, app_name: str = None):
    return driver_factory.restart_driver(device_name, app_name)