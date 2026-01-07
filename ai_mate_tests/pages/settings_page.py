import time
from ai_mate_tests.pages.base_page import BasePage


class SettingsPage(BasePage):
    def open_bluetooth_settings(self):
        """打开蓝牙设置"""
        self.click_by_config("bluetooth_option")

    def get_switch(self):
        """获取蓝牙开关"""
        return self.find_element_by_config("bluetooth_switch")

    def toggle_bluetooth(self, enable):
        """切换蓝牙状态"""
        switch = self.get_switch()
        current = switch.get_attribute("checked") == "true"

        if enable != current:
            switch.click()
            # 快速状态验证
            for _ in range(10):
                if switch.get_attribute("checked") == str(enable).lower():
                    break
                time.sleep(0.1)

    def is_device_connected(self):
        """检查设备连接"""
        try:
            self.find_element_by_config("paired_device_connected", timeout=1)
            return True
        except Exception:
            return False

    def stress_test_bluetooth(self, iterations=50):
        """蓝牙稳定性测试"""
        self.open_bluetooth_settings()
        
        for i in range(1, iterations + 1):
            # 开启蓝牙
            self.toggle_bluetooth(True)
            if not self.is_device_connected():
                raise AssertionError(f"第 {i} 次失败：设备未连接")
            
            # 关闭再开启蓝牙
            self.toggle_bluetooth(False)
            time.sleep(0.2)  # 短暂等待，避免操作过快
            self.toggle_bluetooth(True)
            
            # 等待设备重新连接
            time.sleep(0.5)  # 增加等待时间，确保设备重新连接
            if not self.is_device_connected():
                raise AssertionError(f"第 {i} 次失败：重新打开后未连接")