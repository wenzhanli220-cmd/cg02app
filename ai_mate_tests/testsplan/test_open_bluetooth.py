import pytest
import allure
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_mate_tests.pages.settings_page import SettingsPage
from ai_mate_tests.pages.popup_page import PopupPage


def _run_single_device_test(driver, device_name):
    """单设备测试函数 - 优化版"""
    try:
        settings = SettingsPage(driver)
        popup = PopupPage(driver)
        
        popup.handle_interference_popup()
        settings.stress_test_bluetooth(iterations=5)
        
        print(f"✅ {device_name} - 蓝牙测试通过")
        return device_name, True, None
    except Exception as e:
        print(f"❌ {device_name} - 蓝牙测试失败: {e}")
        return device_name, False, str(e)


@pytest.mark.app_type("settings")
@pytest.mark.bluetooth_test
def test_bluetooth_stability(parallel_drivers):
    """多设备并行蓝牙测试 - 优化版"""
    with allure.step("多设备并行蓝牙稳定性测试"):
        results = {}
        
        # 并行执行所有设备测试
        with ThreadPoolExecutor(max_workers=len(parallel_drivers)) as executor:
            futures = {
                executor.submit(_run_single_device_test, driver, name): name
                for name, driver in parallel_drivers.items()
            }
            
            # 收集结果
            for future in as_completed(futures):
                device_name, success, error = future.result()
                results[device_name] = (success, error)
                
                # Allure 记录
                if success:
                    allure.attach(f"设备 {device_name} 测试通过", name=f"{device_name}_结果")
                else:
                    allure.attach(f"设备 {device_name} 测试失败: {error}", name=f"{device_name}_错误")
        
        # 汇总失败设备
        failed = [name for name, (success, _) in results.items() if not success]
        
        if failed:
            pytest.fail(f"部分设备测试失败: {', '.join(failed)}")
        else:
            print("🎉 所有设备蓝牙测试通过")
