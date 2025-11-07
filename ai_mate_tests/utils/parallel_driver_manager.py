from appium import webdriver
from typing import Dict, List, Optional
import threading
import subprocess

from ai_mate_tests.utils.driver_factory import DriverFactory
from ai_mate_tests.utils.element_manager import ElementManager


class ParallelDriverManager:
    def __init__(self):
        self.driver_factory = DriverFactory()
        self.drivers: Dict[str, webdriver.Remote] = {}
        self.lock = threading.Lock()

    def detect_connected_devices(self) -> List[Dict]:
        """动态检测连接的设备"""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=10
            )

            devices = []
            lines = result.stdout.strip().split('\n')[1:]

            for line in lines:
                if line.strip() and 'device' in line:
                    device_id = line.split('\t')[0]
                    device_info = self.get_device_info(device_id)
                    devices.append(device_info)

            return devices
        except Exception as e:
            print(f"设备检测失败: {e}")
            return []

    @staticmethod
    def get_device_info(device_id: str) -> Dict:
        """获取设备详细信息"""
        try:
            # 获取设备型号
            model_result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                capture_output=True, text=True, timeout=5
            )
            model = model_result.stdout.strip().replace(' ', '_')

            # 获取安卓版本
            version_result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                capture_output=True, text=True, timeout=5
            )
            android_version = version_result.stdout.strip()

            return {
                'device_id': device_id,
                'device_name': model,
                'model': model,
                'platform_version': android_version
            }
        except Exception as e:
            print(f"获取设备 {device_id} 信息失败: {e}")
            return {
                'device_id': device_id,
                'device_name': f"Device_{device_id[-4:]}",
                'model': 'Unknown',
                'platform_version': 'Unknown'
            }

    def find_device_by_udid(self, udid: str) -> Optional[str]:
        """根据 UDID 在配置文件中查找对应的设备名称"""
        try:
            # 获取配置文件中所有设备
            configured_devices = self.driver_factory.config_loader.get_all_devices()

            # 遍历配置中的设备，查找匹配的 UDID
            for device_name in configured_devices:
                device_config = self.driver_factory.config_loader.get_device_config(device_name)
                if device_config and device_config.get('udid') == udid:
                    print(f"✅ UDID 匹配: {udid} -> {device_name}")
                    return device_name

            print(f"❌ 未找到 UDID 为 {udid} 的设备配置")
            return None

        except Exception as e:
            print(f"查找设备配置失败: {e}")
            return None

    def auto_create_drivers(self, app_name: str = "ai_mate") -> List[str]:
        """自动检测设备并创建驱动 - 基于 UDID 匹配"""
        connected_devices = self.detect_connected_devices()
        created_drivers = []

        print(f"🔍 检测到 {len(connected_devices)} 台设备，开始 UDID 匹配...")

        for device_info in connected_devices:
            udid = device_info['device_id']

            # 根据 UDID 在配置文件中查找对应的设备名称
            configured_name = self.find_device_by_udid(udid)

            if configured_name:
                try:
                    driver = self.create_driver(configured_name, app_name)
                    if driver:
                        created_drivers.append(configured_name)
                        print(f"✅ 设备 {configured_name} 驱动创建成功")
                    else:
                        print(f"❌ 设备 {configured_name} 驱动创建失败")
                except Exception as e:
                    print(f"⚠️ 为设备 {configured_name} 创建驱动失败: {e}")
            else:
                print(f"❌ 设备 {device_info['device_name']} (UDID: {udid}) 在配置文件中没有对应的配置")

        return created_drivers

    def create_driver(self, device_name: str, app_name: str = "ai_mate"):
        """创建驱动 - 使用原有逻辑"""
        with self.lock:
            if device_name in self.drivers:
                self.quit_driver(device_name)

            try:
                driver = self.driver_factory.get_driver(device_name, app_name)
                if driver:
                    driver.element_manager = ElementManager(driver.config_loader, device_name)
                    self.drivers[device_name] = driver
                return driver
            except Exception as e:
                print(f"创建驱动失败: {e}")
                return None

    def get_driver(self, device_name: str):
        """获取驱动"""
        with self.lock:
            return self.drivers.get(device_name)

    def get_available_devices(self) -> List[str]:
        """获取可用的配置设备名称"""
        try:
            return self.driver_factory.config_loader.get_all_devices()
        except:
            return []

    def quit_driver(self, device_name: str):
        """退出驱动"""
        with self.lock:
            if device_name in self.drivers:
                try:
                    self.drivers[device_name].quit()
                except Exception as e:
                    print(f"退出驱动失败: {e}")
                del self.drivers[device_name]

    def quit_all_drivers(self):
        """退出所有驱动"""
        with self.lock:
            for device_name in list(self.drivers.keys()):
                self.quit_driver(device_name)

    def get_detected_devices_info(self) -> List[Dict]:
        """获取检测到的设备详细信息"""
        return self.detect_connected_devices()