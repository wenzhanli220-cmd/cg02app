import pytest

from ai_mate_tests.pages.settings_page import SettingsPage
from ai_mate_tests.drivers.appium_driver import get_driver

@pytest.fixture(scope="function")
def settings_driver():
    driver = get_driver("settings")
    yield driver
    driver.quit()



def test_open_bluetooth(settings_driver):
    """
    打开设置 → 进入蓝牙 → 进行 50 次开关蓝牙稳定性测试
    """

    settings = SettingsPage(settings_driver)

    # 调用封装好的稳定性测试方法
    try:
        settings.stress_test_bluetooth(iterations=50)
    except AssertionError as e:
        pytest.fail(f"蓝牙稳定性测试失败: {e}")

    # 如果能执行到这里，说明 50 次循环全部成功
    assert True, "🎉 蓝牙开关稳定性测试完成，所有循环均通过 ✅"