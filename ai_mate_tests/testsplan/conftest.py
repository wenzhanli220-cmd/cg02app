import pytest
import allure
from concurrent.futures import ThreadPoolExecutor, as_completed
from ai_mate_tests.utils.parallel_driver_manager import parallel_driver_manager


def pytest_configure(config):
    """pytest 配置 - xdist 支持"""
    if hasattr(config, 'workerinput'):
        print(f"🚀 xdist worker {config.workerinput['workerid']} 启动")


@pytest.fixture(scope="session")
def device_manager(request):
    """设备管理器 - 管理所有设备"""
    devices = parallel_driver_manager.get_available_devices()
    if not devices:
        pytest.skip("❌ 无可用设备")

    print(f"📱 检测到 {len(devices)} 台设备: {', '.join(devices)}")

    # 在 xdist 中，每个 worker 处理所有设备
    return {
        'all_devices': devices,
        'current_worker': getattr(request.config, 'workerinput', {}).get('workerid', 'master')
    }


@pytest.fixture(scope="function")
def parallel_drivers(request, device_manager):
    """多设备并行驱动 - xdist 兼容"""
    marker = request.node.get_closest_marker("app_type")
    app_type = marker.args[0] if marker else request.config.getoption("--app-type", default="settings")

    all_devices = device_manager['all_devices']

    # 并行创建所有设备驱动
    drivers = {}
    with ThreadPoolExecutor(max_workers=len(all_devices)) as executor:
        future_to_device = {
            executor.submit(parallel_driver_manager.create_driver, device, app_type): device
            for device in all_devices
        }

        for future in as_completed(future_to_device):
            device_name = future_to_device[future]
            try:
                driver = future.result(timeout=30)
                drivers[device_name] = driver
                print(f"✅ {device_manager['current_worker']} - 设备 {device_name} 驱动就绪")
            except Exception as e:
                print(f"⚠️ 设备 {device_name} 驱动创建失败: {e}")

    if not drivers:
        pytest.skip("❌ 所有设备驱动创建失败")

    yield drivers

    # 并行清理所有驱动
    print(f"🧹 {device_manager['current_worker']} - 清理所有设备驱动")
    with ThreadPoolExecutor(max_workers=len(drivers)) as executor:
        for device_name in drivers.keys():
            executor.submit(parallel_driver_manager.quit_driver, device_name)

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