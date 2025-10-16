from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# 引入 PopupPage
from ai_mate_tests.pages.popup_page import PopupPage


class SettingsPage:
    """设置 - 蓝牙页面（集成弹窗自动处理 + 高效等待机制）"""

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
        self.wait = WebDriverWait(driver, 15)
        self.popup = PopupPage(driver)

    # ------------------- 辅助函数 -------------------
    def _quick_check_popup(self, timeout=1.5):
        """
        快速检测弹窗（最多等待 timeout 秒）
        若出现则调用 handle_interference_popup() 并立即返回 True
        若未出现则立即返回 False（不阻塞主流程）
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.popup.handle_interference_popup(timeout=0.5):
                return True
            time.sleep(0.2)
        return False

    def _safe_wait(self, condition, timeout=5):
        """带弹窗检查的安全等待封装"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                return condition(self.driver)
            except Exception:
                self._quick_check_popup(timeout=0.8)
        raise TimeoutException("等待条件超时")

    # ------------------- 蓝牙页面操作 -------------------
    def open_bluetooth_settings(self):
        """进入蓝牙设置"""
        self._quick_check_popup(timeout=1.5)
        self.wait.until(EC.presence_of_element_located(self.BLUETOOTH_OPTION)).click()
        # 打开蓝牙界面后检查一次弹窗
        self._quick_check_popup(timeout=2)

    def get_switch(self):
        """获取蓝牙开关元素"""
        return self.wait.until(EC.presence_of_element_located(self.BLUETOOTH_SWITCH))

    def toggle_bluetooth(self, enable: bool):
        """
        切换蓝牙开关状态（附带快速弹窗检测）
        :param enable: True=打开, False=关闭
        """
        switch = self.get_switch()
        current_status = switch.get_attribute("checked") == "true"

        if enable != current_status:
            switch.click()
            # 点击后检测是否弹窗干扰（短等待）
            self._quick_check_popup(timeout=2)

            # 使用非阻塞等待验证状态变化
            self._safe_wait(
                lambda d: switch.get_attribute("checked") == str(enable).lower(),
                timeout=5
            )

    def is_device_connected(self):
        """检测是否有配对设备连接"""
        try:
            self.wait.until(EC.presence_of_element_located(self.PAIRED_DEVICE_CONNECTED))
            return True
        except TimeoutException:
            return False

    # ------------------- 稳定性测试 -------------------
    def stress_test_bluetooth(self, iterations: int = 50):
        """
        蓝牙开关稳定性测试：开关多次并验证连接状态。
        自动检测干扰弹窗（短暂轮询），在无弹窗时快速继续。
        """
        self.open_bluetooth_settings()

        for i in range(1, iterations + 1):
            print(f"🔄 第 {i} 次蓝牙开关测试")

            # 打开 → 检查连接
            self.toggle_bluetooth(enable=True)
            if not self.is_device_connected():
                raise AssertionError(f"❌ 第 {i} 次失败：设备未连接")

            # 关闭 → 再打开 → 检查连接
            self.toggle_bluetooth(enable=False)
            self.toggle_bluetooth(enable=True)
            if not self.is_device_connected():
                raise AssertionError(f"❌ 第 {i} 次失败：重新打开后未连接")

            print(f"✅ 第 {i} 次测试通过")

        print(f"🎉 蓝牙稳定性测试完成，共 {iterations} 次均成功连接")
