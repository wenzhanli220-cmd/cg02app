from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SettingsPage:
    """设置 - 蓝牙页面"""

    BLUETOOTH_OPTION = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@resource-id='android:id/title' and @text='蓝牙']"
    )
    BLUETOOTH_SWITCH = (AppiumBy.CLASS_NAME, "android.widget.Switch")
    PAIRED_DEVICE_CONNECTED = (
        AppiumBy.XPATH,
        "//android.widget.TextView[@resource-id='android:id/summary' and contains(@text,'使用中，电池电量')]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def open_bluetooth_settings(self):
        """点击设置中的蓝牙选项"""
        self.wait.until(EC.presence_of_element_located(self.BLUETOOTH_OPTION)).click()

    def get_switch(self):
        """获取蓝牙开关元素"""
        return self.wait.until(EC.presence_of_element_located(self.BLUETOOTH_SWITCH))

    def toggle_bluetooth(self, enable: bool):
        """
        切换蓝牙开关
        :param enable: True=打开蓝牙, False=关闭蓝牙
        """
        switch = self.get_switch()
        current_status = switch.get_attribute("checked") == "true"

        if enable and not current_status:
            switch.click()
            self.wait.until(lambda d: switch.get_attribute("checked") == "true")

        elif not enable and current_status:
            switch.click()
            self.wait.until(lambda d: switch.get_attribute("checked") == "false")

    def is_device_connected(self):
        """检查是否有已连接的设备"""
        try:
            self.wait.until(EC.presence_of_element_located(self.PAIRED_DEVICE_CONNECTED))
            return True
        except:
            return False

    def stress_test_bluetooth(self, iterations: int = 50):
        """
        稳定性测试：开关蓝牙 N 次，每次都验证已配对设备能否成功连接
        """
        # 进入蓝牙界面
        self.open_bluetooth_settings()

        for i in range(1, iterations + 1):
            print(f"🔄 第 {i} 次蓝牙开关测试")

            # Step 1: 确保先打开蓝牙并检查是否有设备连接
            self.toggle_bluetooth(enable=True)
            if not self.is_device_connected():
                raise AssertionError(f"❌ 第 {i} 次测试失败：设备未连接")

            # Step 2: 关闭蓝牙
            self.toggle_bluetooth(enable=False)

            # Step 3: 再次打开蓝牙并检查连接
            self.toggle_bluetooth(enable=True)
            if not self.is_device_connected():
                raise AssertionError(f"❌ 第 {i} 次测试失败：设备未连接")

            print(f"✅ 第 {i} 次测试通过")

        print(f"🎉 蓝牙开关稳定性测试完成，连续 {iterations} 次均成功连接")