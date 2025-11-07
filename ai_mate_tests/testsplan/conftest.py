
import pytest
import allure
import time

from ai_mate_tests.utils.parallel_driver_manager import ParallelDriverManager

parallel_driver_manager = ParallelDriverManager()

def pytest_configure(config):
    """pytest 配置 - xdist 支持"""
    if hasattr(config, 'workerinput'):
        print(f"🚀 xdist worker {config.workerinput['workerid']} 启动")

@pytest.fixture(scope="function")
def device_manager():
    """设备管理器 - 智能识别设备"""
    # 自动检测设备
    detected_devices = parallel_driver_manager.detect_connected_devices()
    if detected_devices:
        print(f"🔍 检测到 {len(detected_devices)} 台设备:")
        for device in detected_devices:
            print(f"   - {device['device_name']} (UDID: {device['device_id']})")

    return {
        'detected_devices': detected_devices
    }
@pytest.fixture(scope="function")
def parallel_drivers(request, device_manager):
    """完整测试专用驱动 - 多设备"""
    print("🔄 准备完整测试设备...")

    # 获取应用类型
    marker = request.node.get_closest_marker("app_type")
    app_type = marker.args[0] if marker else "settings"

    # 清理所有驱动（完整测试需要干净环境）
    parallel_driver_manager.quit_all_drivers()
    time.sleep(1)

    # 创建所有设备驱动
    created_devices = parallel_driver_manager.auto_create_drivers(app_type)

    if not created_devices:
        pytest.skip("❌ 无法创建任何设备驱动")

    # 获取驱动
    drivers = {}
    for device_name in created_devices:
        driver = parallel_driver_manager.get_driver(device_name)
        if driver:
            drivers[device_name] = driver
            print(f"✅ {device_name} 就绪")

    # 等待稳定
    time.sleep(2)

    yield drivers

    # 清理所有驱动
    for device_name in drivers.keys():
        parallel_driver_manager.quit_driver(device_name)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """多设备截图支持"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and ('parallel_drivers' in item.funcargs):
        drivers = item.funcargs['parallel_drivers']
        if report.failed or report.outcome in ("failed", "error"):
            for device_name, driver in drivers.items():
                try:
                    screenshot = driver.get_screenshot_as_png()
                    name = f"{device_name}_{report.nodeid.replace(':', '_')}"
                    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
                except Exception as e:
                    print(f"⚠️ 截图失败: {device_name} - {e}")


def pytest_addoption(parser):
    parser.addoption("--app-type", action="store", default="settings", help="应用类型: settings 或 ai_mate")