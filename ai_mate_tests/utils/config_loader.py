import yaml
import os
from typing import Dict, Any, List, Optional
from appium.webdriver.common.appiumby import AppiumBy
from yaml import YAMLError


class ConfigLoader:
    # 类常量：默认配置
    DEFAULT_CONFIG = {
        'default_appium_server': 'http://localhost:4723/wd/hub',
        'default_app': 'ai_mate'
    }

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = self._resolve_absolute_path(config_path)
        self.config = self._load_config()
        # 预构建元素定位映射，提高查询效率
        self.element_mapping = self._build_element_mapping()

    @staticmethod
    def _resolve_absolute_path(config_path: str) -> str:
        """将相对路径转换为绝对路径"""
        if not os.path.isabs(config_path):
            return os.path.abspath(os.path.join(os.getcwd(), config_path))
        return config_path

    def _load_config(self) -> Dict[str, Any]:
        """加载YAML配置文件，完善异常处理"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                if not isinstance(config_data, dict):
                    raise ValueError(f"配置文件格式错误，预期字典类型，实际为: {type(config_data)}")
                return config_data
        except YAMLError as e:
            raise RuntimeError(f"YAML配置解析错误: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {str(e)}") from e

    def _build_element_mapping(self) -> Dict[str, Dict[str, Any]]:
        """预构建元素定位映射，key为element_key，value为定位信息"""
        mapping = {}
        devices = self.config.get('devices', {})

        for device_name, device_config in devices.items():
            elements = device_config.get('elements', {})
            for page, page_elements in elements.items():
                for element_key, element_info in page_elements.items():
                    # 存储设备、页面和定位信息，方便溯源
                    mapping[f"{device_name}_{element_key}"] = {
                        'by': element_info.get('by'),
                        'value': element_info.get('value'),
                        'page': page,
                        'device': device_name
                    }
        return mapping

    def get_appium_servers(self) -> Dict[str, str]:
        """获取所有Appium服务器地址"""
        return self.config.get('appium_servers', {})

    def get_all_devices(self) -> List[str]:
        """获取所有设备名称列表"""
        return list(self.config.get('devices', {}).keys())

    def get_device_capabilities(self, device_name: str) -> Dict[str, Any]:
        """获取指定设备的完整配置，优化配置合并逻辑"""
        devices = self.config.get('devices', {})
        if device_name not in devices:
            raise ValueError(f"设备 {device_name} 不在配置中 (配置路径: {self.config_path})")

        device_config = devices[device_name].copy()
        app_configs = self.config.get('app_configs', {})
        driver_options = self.config.get('driver_options', {})

        # 获取默认应用配置
        default_app = self.config.get('default_app', self.DEFAULT_CONFIG['default_app'])

        # 合并应用配置（仅补充未设置的键）
        app_config = app_configs.get(default_app, {})
        for key in ['appPackage', 'appActivity']:
            if key not in device_config:
                # 兼容旧配置中的下划线命名
                device_config[key] = app_config.get(key.lower(), None)

        # 合并驱动选项（仅补充未设置的键）
        for key, value in driver_options.items():
            if key not in device_config:
                device_config[key] = value

        return device_config

    def get_appium_server_url(self, device_name: str) -> str:
        """获取指定设备的Appium服务器URL，优先使用配置中的默认值"""
        # 1. 检查设备配置中是否有独立的appium_server_url
        device_config = self.config['devices'].get(device_name, {})
        if 'appium_server_url' in device_config:
            return device_config['appium_server_url']

        # 2. 检查顶层appium_servers配置
        appium_servers = self.get_appium_servers()
        if device_name in appium_servers:
            return appium_servers[device_name]

        # 3. 使用配置文件中的默认值，最后 fallback 到类常量
        return self.config.get('default_appium_server', self.DEFAULT_CONFIG['default_appium_server'])

    def get_appium_server_by_device(self, device_name: str) -> str:
        """兼容方法：根据设备名称获取对应的Appium服务器URL"""
        return self.get_appium_server_url(device_name)

    def get_element_locator(self, device_name: str, element_key: str) -> Dict[str, Any]:
        """获取指定设备的元素定位配置，使用预构建的映射提高效率"""
        key = f"{device_name}_{element_key}"
        if key in self.element_mapping:
            return self.element_mapping[key]

        raise ValueError(
            f"元素 {element_key} 在设备 {device_name} 中未找到 "
            f"(配置路径: {self.config_path})"
        )

    def get_element_by_page(self, device_name: str, page: str, element_key: str) -> Dict[str, Any]:
        """按页面获取元素定位配置，增加错误上下文"""
        devices = self.config.get('devices', {})
        device_config = devices.get(device_name, {})
        elements = device_config.get('elements', {})
        page_elements = elements.get(page, {})

        if element_key not in page_elements:
            raise ValueError(
                f"元素 {element_key} 在设备 {device_name} 的页面 {page} 中未找到 "
                f"(配置路径: {self.config_path})"
            )

        element_config = page_elements[element_key]
        return {
            'by': element_config.get('by'),
            'value': element_config.get('value')
        }

    def get_success_texts(self, device_name: str) -> List[Dict[str, str]]:
        """获取成功验证文本配置"""
        try:
            locator = self.get_element_locator(device_name, 'success_texts')
            # 从原始配置中获取完整数据（因为映射中只存储了基础定位信息）
            devices = self.config.get('devices', {})
            return devices[device_name]['elements'][locator['page']]['success_texts']
        except (KeyError, ValueError):
            return []

    def get_popup_close_coords(self, device_name: str) -> Optional[Dict[str, int]]:
        """获取弹窗关闭坐标"""
        try:
            locator = self.get_element_locator(device_name, 'popup_close_coords')
            devices = self.config.get('devices', {})
            coords = devices[device_name]['elements'][locator['page']]['popup_close_coords']
            return {'x': coords.get('x'), 'y': coords.get('y')}
        except (KeyError, ValueError):
            return None

    def get_app_config(self, app_name: str) -> Dict[str, str]:
        """获取应用配置"""
        app_configs = self.config.get('app_configs', {})
        return app_configs.get(app_name, {})

    def get_driver_options(self) -> Dict[str, Any]:
        """获取驱动选项"""
        return self.config.get('driver_options', {})

    def convert_locator_to_appium_format(self, locator_config: Dict[str, Any]) -> tuple:
        """将定位配置转换为Appium格式 (by, value) - 改为实例方法提高灵活性"""
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
            raise ValueError(f"无效的定位配置: {locator_config} (配置路径: {self.config_path})")

        if by_type not in by_mapping:
            raise ValueError(
                f"不支持的定位方式: {by_type}，支持的类型: {list(by_mapping.keys())} "
                f"(配置路径: {self.config_path})"
            )

        return by_mapping[by_type], value
