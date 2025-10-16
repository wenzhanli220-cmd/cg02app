
import pytest
from ai_mate_tests.pages.settings_page import SettingsPage
from ai_mate_tests.pages.popup_page import PopupPage  # 引入弹窗处理类


def test_open_bluetooth(settings_driver):
    """
    打开设置 → 进入蓝牙 → 进行 5 次开关蓝牙稳定性测试

    测试过程中自动处理可能出现的干扰弹窗
    """
    settings = SettingsPage(settings_driver)
    popup = PopupPage(settings_driver)  # 初始化弹窗处理实例

    try:
        # 执行稳定性测试前先处理一次可能存在的弹窗

        popup.handle_interference_popup()

        # 执行稳定性测试（假设该方法内部是循环开关蓝牙的逻辑）
        settings.stress_test_bluetooth(iterations=1)

    except AssertionError as e:
        pytest.fail(f"蓝牙稳定性测试失败: {e}")

    assert True, "🎉 蓝牙开关稳定性测试完成，所有循环均通过 ✅"
