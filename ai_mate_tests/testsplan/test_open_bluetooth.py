import pytest
import allure

from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_mate_tests.pages.settings_page import SettingsPage
from ai_mate_tests.pages.popup_page import PopupPage


def _run_single_device_test(driver, device_name):
    """单设备测试函数"""
    try:
        settings = SettingsPage(driver)
        popup = PopupPage(driver)

        popup.handle_interference_popup()
        settings.stress_test_bluetooth(iterations=5)

        print(f"✅ {device_name} - 蓝牙测试通过")
        return device_name, True, None
    except Exception as e:
        print(f"❌ {device_name} - 蓝牙测试失败: {e}")
        raise RuntimeError(f"{device_name} 测试失败: {e}")


@pytest.mark.app_type("settings")
@pytest.mark.bluetooth_test
def test_bluetooth_stability(parallel_drivers):
    """多设备并行蓝牙测试 - xdist 兼容"""
    with allure.step("多设备并行蓝牙稳定性测试"):
        iterations = 5
        print(f"📊 开始蓝牙稳定性测试，每个设备执行 {iterations} 次测试")
        results = {}

        # 并行执行所有设备测试
        with ThreadPoolExecutor(max_workers=len(parallel_drivers)) as executor:
            future_to_device = {
                executor.submit(_run_single_device_test, driver, device_name): device_name
                for device_name, driver in parallel_drivers.items()
            }

            for future in as_completed(future_to_device):
                device_name, success, error = future.result()
                results[device_name] = (success, error)

                # 记录到 Allure
                if success:
                    allure.attach(f"设备 {device_name} 测试通过", name=f"{device_name}_结果")
                else:
                    allure.attach(f"设备 {device_name} 测试失败: {error}", name=f"{device_name}_错误")

        # 汇总结果
        failed_devices = [name for name, (success, error) in results.items() if not success]

        if failed_devices:
            pytest.fail(f"部分设备测试失败: {', '.join(failed_devices)}")

        else:
            print("🎉 所有设备蓝牙测试通过")
