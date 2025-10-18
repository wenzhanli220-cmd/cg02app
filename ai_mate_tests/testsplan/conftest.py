import allure
import pytest
from ai_mate_tests.drivers.appium_driver import get_driver


# 定义 settings 驱动的 Fixture
@pytest.fixture(scope="function")
def settings_driver():
    driver = get_driver("settings")
    yield driver
    try:
        driver.quit()
    except Exception as e:
        print(f"⚠️ 关闭settings_driver时出现异常: {e}")


# 定义 ai_mate 驱动的 Fixture
@pytest.fixture(scope="function")
def ai_mate_driver():
    driver = get_driver("ai_mate")
    yield driver
    try:
        driver.quit()
    except Exception as e:
        print(f"⚠️ 关闭ai_mate_driver时出现异常: {e}")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # 只在测试调用阶段且失败时截图
    if report.when == "call" and report.failed:
        driver = None
        for driver_name in ["driver", "settings_driver", "ai_mate_driver"]:
            potential_driver = item.funcargs.get(driver_name)
            if potential_driver:
                driver = potential_driver
                break

        if driver:
            try:
                # 更安全的方式来检查驱动是否仍然有效
                # 尝试获取一个简单的属性来验证会话状态
                _ = driver.session_id  # 这会检查会话是否仍然有效
                name = f"{report.nodeid}_{report.when}"
                screenshot = driver.get_screenshot_as_png()
                allure.attach(
                    screenshot,
                    name=name,
                    attachment_type=allure.attachment_type.PNG
                )
                print(f"✅ 已为失败测试截图: {name}")
            except Exception as e:
                # 如果驱动无效或截图失败，静默处理
                print(f"⚠️ 无法为失败测试截图: {e}")