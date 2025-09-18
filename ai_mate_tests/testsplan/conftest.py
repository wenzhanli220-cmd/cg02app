import allure
import pytest

from ai_mate_tests.drivers.appium_driver import get_driver


@pytest.fixture(scope="function")
def driver():
    """初始化和关闭 driver，每个测试方法独立运行"""
    driver = get_driver()
    yield driver
    driver.quit()




@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    每个阶段都截图：
    - setup 阶段
    - call 阶段（用例执行）
    - teardown 阶段
    """
    outcome = yield
    report = outcome.get_result()

    driver = item.funcargs.get("driver", None)
    if driver:
        # 生成附件名：用例名 + 阶段
        name = f"{report.nodeid}_{report.when}"
        screenshot = driver.get_screenshot_as_png()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )