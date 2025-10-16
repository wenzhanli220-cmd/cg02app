import allure
import pytest


from ai_mate_tests.drivers.appium_driver import get_driver


@pytest.fixture(scope="function")
def settings_driver():
    driver = get_driver("settings")
    yield driver
    driver.quit()

# 定义 ai_mate 驱动的 Fixture（假设另一个用例需要）
@pytest.fixture(scope="function")
def ai_mate_driver():
    driver = get_driver("ai_mate")
    yield driver
    driver.quit()

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    driver = (
        item.funcargs.get("driver")
        or item.funcargs.get("settings_driver")
        or item.funcargs.get("ai_mate_driver")
    )

    if driver:
        name = f"{report.nodeid}_{report.when}"
        screenshot = driver.get_screenshot_as_png()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )