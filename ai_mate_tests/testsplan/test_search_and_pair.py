import pytest
import allure
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_mate_tests.pages.device_page import DevicePage
from ai_mate_tests.pages.popup_page import PopupPage
from ai_mate_tests.pages.welcome_page import WelcomePage


def _run_single_pairing_test(driver, device_name):
    """单设备配对测试函数"""
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
        raise RuntimeError(f"{device_name} 测试失败: {e}")



@pytest.mark.app_type("ai_mate")
@pytest.mark.pairing_test
def test_device_pairing_multi_device(parallel_drivers):
    """多设备并行配对测试 - xdist 兼容"""
    with allure.step("多设备并行配对测试"):
        results = {}

        # 并行执行所有设备配对
        with ThreadPoolExecutor(max_workers=len(parallel_drivers)) as executor:
            future_to_device = {
                executor.submit(_run_single_pairing_test, driver, device_name): device_name
                for device_name, driver in parallel_drivers.items()
            }

            for future in as_completed(future_to_device):
                device_name, success, error = future.result()
                results[device_name] = (success, error)

                # 记录到 Allure
                if success:
                    allure.attach(f"设备 {device_name} 配对成功", name=f"{device_name}_结果")
                else:
                    allure.attach(f"设备 {device_name} 配对失败: {error}", name=f"{device_name}_错误")

        # 汇总结果
        failed_devices = [name for name, (success, error) in results.items() if not success]

        if failed_devices:
            pytest.fail(f"部分设备测试失败: {', '.join(failed_devices)}")

        else:
            print("🎉 所有设备配对成功")


@pytest.mark.app_type("ai_mate")
def test_quick_pairing_multi_device(parallel_drivers):
    """多设备快速配对测试 - xdist 兼容"""
    failed_devices = []

    for device_name, driver in parallel_drivers.items():
        try:
            device = DevicePage(driver)
            popup = PopupPage(driver)

            popup.handle_interference_popup()

            # 快速配对流程
            assert device.complete_pairing_flow(), f"{device_name} 快速配对失败"

            print(f"✅ {device_name} - 快速配对成功")
        except Exception as e:
            print(f"❌ {device_name} - 快速配对失败: {e}")
            failed_devices.append(device_name)

    if failed_devices:
        pytest.fail(f"快速测试失败设备: {', '.join(failed_devices)}")

