import pytest
import allure
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_mate_tests.pages.device_page import DevicePage
from ai_mate_tests.pages.popup_page import PopupPage
from ai_mate_tests.pages.welcome_page import WelcomePage


def _run_single_pairing_test(driver, device_name):
    """单设备配对测试函数 - 优化版"""
    try:
        welcome = WelcomePage(driver)
        device = DevicePage(driver)
        popup = PopupPage(driver)
        
        popup.handle_interference_popup()
        welcome.accept_all()
        popup.handle_interference_popup()
        
        device.search_device()
        device.pair_device()
        
        assert device.is_paired_success(timeout=30), f"{device_name} 配对失败"
        
        print(f"✅ {device_name} - 配对成功")
        return device_name, True, None
    except Exception as e:
        print(f"❌ {device_name} - 配对失败: {e}")
        return device_name, False, str(e)


@pytest.mark.app_type("ai_mate")
@pytest.mark.pairing_test
def test_device_pairing_multi_device(parallel_drivers):
    """多设备并行配对测试 - 优化版"""
    with allure.step("多设备并行配对测试"):
        results = {}
        
        # 并行执行所有设备配对
        with ThreadPoolExecutor(max_workers=len(parallel_drivers)) as executor:
            futures = {
                executor.submit(_run_single_pairing_test, driver, name): name
                for name, driver in parallel_drivers.items()
            }
            
            # 收集结果
            for future in as_completed(futures):
                device_name, success, error = future.result()
                results[device_name] = (success, error)
                
                # Allure 记录
                if success:
                    allure.attach(f"设备 {device_name} 配对成功", name=f"{device_name}_结果")
                else:
                    allure.attach(f"设备 {device_name} 配对失败: {error}", name=f"{device_name}_错误")
        
        # 汇总失败设备
        failed = [name for name, (success, _) in results.items() if not success]
        
        if failed:
            pytest.fail(f"部分设备测试失败: {', '.join(failed)}")
        else:
            print("🎉 所有设备配对成功")


