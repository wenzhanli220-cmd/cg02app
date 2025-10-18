# utils/config_loader.py
import yaml
import os
from typing import Dict, Any, List, Optional
from appium.webdriver.common.appiumby import AppiumBy


class ConfigLoader:
    def __init__(self, config_path: str = None):
        # 如果没有指定路径，尝试多个可能的位置
        if config_path is None:
            # 尝试从项目根目录开始查找
            possible_paths = [
                "utils/config.yaml",  # 当前目录下的utils
                "config.yaml",  # 当前目录
                "../utils/config.yaml",  # 上级目录的utils
                "./utils/config.yaml",  # 明确当前目录下的utils
                os.path.join(os.path.dirname(__file__), "config.yaml"),  # 与config_loader.py同目录
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.config_path = path
                    print(f"✅ 找到配置文件: {os.path.abspath(path)}")
                    break
            else:
                # 如果都没找到，使用默认路径并打印错误
                self.config_path = "utils/config.yaml"
                print(f"❌ 未找到配置文件，尝试过的路径: {possible_paths}")
        else:
            self.config_path = config_path

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        if not os.path.exists(self.config_path):
            # 提供更详细的错误信息
            current_dir = os.getcwd()
            abs_config_path = os.path.abspath(self.config_path)
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"绝对路径: {abs_config_path}\n"
                f"当前工作目录: {current_dir}\n"
                f"请确保config.yaml文件位于正确位置"
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                print(f"✅ 配置文件加载成功: {self.config_path}")
                return config
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            raise

    def get_appium_servers(self) -> Dict[str, str]:
        """获取所有Appium服务器地址"""
        return self.config.get('appium_servers', {})

    def get_all_devices(self) -> List[str]:
        """获取所有设备名称列表"""
        return list(self.config.get('devices', {}).keys())

    def get_device_config(self, device_name: str) -> Dict[str, Any]:
        """获取指定设备的完整配置"""
        devices = self.config.get('devices', {})
        if device_name not in devices:
            raise ValueError(f"设备 {device_name} 不在配置中")
        return devices[device_name].copy()

    def get_device_capabilities(self, device_name: str) -> Dict[str, Any]:
        """获取指定设备的驱动能力配置"""
        device_config = self.get_device_config(device_name)

        # 合并应用配置
        app_configs = self.config.get('app_configs', {})
        driver_options = self.config.get('driver_options', {})

        # 设置默认应用配置
        if 'app_package' not in device_config:
            device_config['appPackage'] = app_configs.get('ai_mate', {}).get('app_package')
        if 'app_activity' not in device_config:
            device_config['appActivity'] = app_configs.get('ai_mate', {}).get('app_activity')

        # 合并驱动选项
        device_config.update(driver_options)

        return device_config

    def get_appium_server_url(self, device_name: str) -> str:
        """获取指定设备的Appium服务器URL"""
        # 首先检查设备配置中是否有独立的appium_server_url
        device_config = self.get_device_config(device_name)
        if 'appium_server_url' in device_config:
            return device_config['appium_server_url']

        # 如果没有，使用顶层的appium_servers配置
        appium_servers = self.get_appium_servers()
        if device_name in appium_servers:
            return appium_servers[device_name]

        # 如果都没有配置，使用默认值
        return 'http://localhost:4723/wd/hub'

    def get_device_elements(self, device_name: str) -> Dict[str, Any]:
        """获取指定设备的所有元素配置"""
        device_config = self.get_device_config(device_name)
        return device_config.get('elements', {})

    def get_element_locator(self, device_name: str, element_key: str) -> Dict[str, Any]:
        """获取指定设备的元素定位配置（自动搜索所有页面）"""
        elements = self.get_device_elements(device_name)

        if not elements:
            raise ValueError(f"设备 {device_name} 没有配置元素")

        # 遍历所有页面查找元素
        for page, page_elements in elements.items():
            if element_key in page_elements:
                element_config = page_elements[element_key]
                return {
                    'by': element_config.get('by'),
                    'value': element_config.get('value'),
                    'page': page
                }

        raise ValueError(f"元素 {element_key} 在设备 {device_name} 中未找到")

    def get_element_by_page(self, device_name: str, page: str, element_key: str) -> Dict[str, Any]:
        """按页面获取元素定位配置"""
        elements = self.get_device_elements(device_name)

        if not elements:
            raise ValueError(f"设备 {device_name} 没有配置元素")

        page_elements = elements.get(page, {})

        if element_key not in page_elements:
            raise ValueError(f"元素 {element_key} 在页面 {page} 中未找到")

        element_config = page_elements[element_key]
        return {
            'by': element_config.get('by'),
            'value': element_config.get('value')
        }

    def get_success_texts(self, device_name: str) -> List[Dict[str, str]]:
        """获取成功验证文本配置"""
        elements = self.get_device_elements(device_name)

        if not elements:
            return []

        # 查找success_texts
        for page, page_elements in elements.items():
            if 'success_texts' in page_elements:
                return page_elements['success_texts']

        return []

    def get_popup_close_coords(self, device_name: str) -> Optional[Dict[str, int]]:
        """获取弹窗关闭坐标"""
        elements = self.get_device_elements(device_name)

        if not elements:
            return None

        # 查找popup_close_coords
        for page, page_elements in elements.items():
            if 'popup_close_coords' in page_elements:
                coords = page_elements['popup_close_coords']
                return {'x': coords.get('x'), 'y': coords.get('y')}

        return None

    def get_app_config(self, app_name: str) -> Dict[str, str]:
        """获取应用配置"""
        app_configs = self.config.get('app_configs', {})
        return app_configs.get(app_name, {})

    def get_driver_options(self) -> Dict[str, Any]:
        """获取驱动选项"""
        return self.config.get('driver_options', {})

    def get_all_pages_for_device(self, device_name: str) -> List[str]:
        """获取指定设备的所有页面名称"""
        elements = self.get_device_elements(device_name)
        return list(elements.keys()) if elements else []

    def get_page_elements(self, device_name: str, page: str) -> Dict[str, Any]:
        """获取指定设备指定页面的所有元素"""
        elements = self.get_device_elements(device_name)
        return elements.get(page, {})

    def validate_device_config(self, device_name: str) -> bool:
        """验证设备配置是否完整"""
        try:
            device_config = self.get_device_config(device_name)
            required_fields = ['udid', 'platform_name', 'platform_version', 'device_name']

            for field in required_fields:
                if field not in device_config:
                    print(f"警告: 设备 {device_name} 缺少必要字段: {field}")
                    return False

            # 检查是否有元素配置
            elements = self.get_device_elements(device_name)
            if not elements:
                print(f"警告: 设备 {device_name} 没有配置元素")
                return False

            return True

        except Exception as e:
            print(f"验证设备 {device_name} 配置时出错: {e}")
            return False

    @staticmethod
    def convert_locator_to_appium_format(locator_config: Dict[str, Any]) -> tuple:
        """将定位配置转换为Appium格式 (by, value) - 静态方法"""
        by_mapping = {
            'xpath': AppiumBy.XPATH,
            'accessibility_id': AppiumBy.ACCESSIBILITY_ID,
            'android_uiautomator': AppiumBy.ANDROID_UIAUTOMATOR,
            'class_name': AppiumBy.CLASS_NAME,
            'id': AppiumBy.ID
        }

        by_type = locator_config.get('by')
        value = locator_config.get('value')

        if not by_type or not value:
            raise ValueError(f"无效的定位配置: {locator_config}")

        if by_type not in by_mapping:
            raise ValueError(f"不支持的定位方式: {by_type}")

        return by_mapping[by_type], value

    def print_device_info(self, device_name: str):
        """打印设备配置信息"""
        device_config = self.get_device_config(device_name)
        elements = self.get_device_elements(device_name)

        print(f"\n=== 设备 {device_name} 配置信息 ===")
        print(f"UDID: {device_config.get('udid')}")
        print(f"平台: {device_config.get('platform_name')} {device_config.get('platform_version')}")
        print(f"设备名: {device_config.get('device_name')}")
        print(f"Appium服务器: {self.get_appium_server_url(device_name)}")
        print(f"页面数量: {len(elements)}")

        for page_name, page_elements in elements.items():
            print(f"  - {page_name}: {len(page_elements)} 个元素")

        print("==============================\n")


# 创建全局实例
config_loader = ConfigLoader()


# 便捷函数
def get_driver_options():
    return config_loader.get_driver_options()


def get_app_config(app_name):
    return config_loader.get_app_config(app_name)


def get_all_devices():
    return config_loader.get_all_devices()


def validate_all_devices():
    """验证所有设备配置"""
    devices = get_all_devices()
    results = {}

    for device in devices:
        results[device] = config_loader.validate_device_config(device)
        if results[device]:
            config_loader.print_device_info(device)
        else:
            print(f"❌ 设备 {device} 配置验证失败")

    return results