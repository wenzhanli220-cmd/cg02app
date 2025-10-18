import allure
import pytest
from ai_mate_tests.utils.parallel_driver_manager import parallel_driver_manager


class DriverFixtureManager:
    """
    Fixture 管理器
    基于现有的 ParallelDriverManager 提供测试友好的接口
    """

    def __init__(self):
        self.manager = parallel_driver_manager

    def create_driver(self, device_name, app_type):
        """创建驱动，适配现有的 ParallelDriverManager"""
        # 将 app_type 映射到 ParallelDriverManager 期望的格式
        app_name = "ai_mate" if app_type == "ai_mate" else "settings"
        return self.manager.create_driver(device_name, app_name)

    def quit_driver(self, device_name):
        """关闭单个驱动"""
        self.manager.quit_driver(device_name)

    def quit_all_drivers(self):
        """关闭所有驱动"""
        self.manager.quit_all_drivers()


# ==================== 会话级 Fixtures ====================

@pytest.fixture(scope="session")
def driver_fixture_manager():
    """
    会话级驱动管理器 fixture
    在整个测试会话期间管理驱动生命周期
    """
    manager = DriverFixtureManager()
    yield manager
    # 测试会话结束时清理所有驱动
    manager.quit_all_drivers()


# ==================== 单设备测试 Fixtures ====================

@pytest.fixture(scope="function")
def settings_driver(driver_fixture_manager):
    """
    设置应用驱动 - 单设备 (device1)
    用于系统设置相关的测试
    """
    driver = driver_fixture_manager.create_driver("device1", "settings")
    yield driver
    driver_fixture_manager.quit_driver("device1")


@pytest.fixture(scope="function")
def ai_mate_driver(driver_fixture_manager):
    """
    AI Mate 应用驱动 - 单设备 (device1)
    用于 AI Mate 应用功能测试
    """
    driver = driver_fixture_manager.create_driver("device1", "ai_mate")
    yield driver
    driver_fixture_manager.quit_driver("device1")


# ==================== 多设备并行测试 Fixtures ====================

@pytest.fixture(scope="function")
def multi_settings_drivers(driver_fixture_manager):
    """
    多设备设置应用驱动
    返回所有设备的设置应用驱动字典
    """
    # 获取所有可用设备
    available_devices = driver_fixture_manager.manager.get_available_devices()
    drivers = {}

    # 为每个设备创建设置应用驱动
    for device_name in available_devices:
        try:
            driver = driver_fixture_manager.create_driver(device_name, "settings")
            drivers[device_name] = driver
        except Exception as e:
            print(f"❌ 设备 {device_name} 设置应用驱动创建失败: {e}")

    yield drivers
    driver_fixture_manager.quit_all_drivers()


@pytest.fixture(scope="function")
def multi_ai_mate_drivers(driver_fixture_manager):
    """
    多设备 AI Mate 应用驱动
    返回所有设备的 AI Mate 应用驱动字典
    """
    # 获取所有可用设备
    available_devices = driver_fixture_manager.manager.get_available_devices()
    drivers = {}

    # 为每个设备创建 AI Mate 应用驱动
    for device_name in available_devices:
        try:
            driver = driver_fixture_manager.create_driver(device_name, "ai_mate")
            drivers[device_name] = driver
        except Exception as e:
            print(f"❌ 设备 {device_name} AI Mate 应用驱动创建失败: {e}")

    yield drivers
    driver_fixture_manager.quit_all_drivers()


# ==================== 动态设备选择 Fixtures ====================

def pytest_addoption(parser):
    """添加 pytest 命令行选项"""
    parser.addoption(
        "--device",
        action="store",
        default="device1",
        help="指定测试设备: device1, device2"
    )
    parser.addoption(
        "--app-type",
        action="store",
        default="ai_mate",
        help="指定应用类型: ai_mate, settings"
    )
    parser.addoption(
        "--parallel",
        action="store_true",
        default=False,
        help="启用多设备并行测试"
    )


@pytest.fixture(scope="function")
def device_name(request):
    """获取命令行指定的设备名称"""
    return request.config.getoption("--device")


@pytest.fixture(scope="function")
def app_type(request):
    """获取命令行指定的应用类型"""
    return request.config.getoption("--app-type")


@pytest.fixture(scope="function")
def parallel_mode(request):
    """获取并行模式设置"""
    return request.config.getoption("--parallel")


@pytest.fixture(scope="function")
def dynamic_driver(driver_fixture_manager, device_name, app_type):
    """
    动态驱动选择
    根据命令行参数选择设备和应用类型
    """
    driver = driver_fixture_manager.create_driver(device_name, app_type)
    yield driver
    driver_fixture_manager.quit_driver(device_name)


# ==================== 智能驱动选择 Fixture ====================

@pytest.fixture(scope="function")
def smart_driver(driver_fixture_manager, device_name, app_type, parallel_mode):
    """
    智能驱动选择
    根据并行模式自动选择单设备或多设备驱动
    """
    if parallel_mode:
        # 并行模式：返回所有设备的驱动
        available_devices = driver_fixture_manager.manager.get_available_devices()
        drivers = {}
        for dev_name in available_devices:
            try:
                driver = driver_fixture_manager.create_driver(dev_name, app_type)
                drivers[dev_name] = driver
            except Exception as e:
                print(f"❌ 设备 {dev_name} 驱动创建失败: {e}")
        yield drivers
        driver_fixture_manager.quit_all_drivers()
    else:
        # 单设备模式：返回指定设备的驱动
        driver = driver_fixture_manager.create_driver(device_name, app_type)
        yield driver
        driver_fixture_manager.quit_driver(device_name)


# ==================== 测试报告和截图处理 ====================

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告钩子函数
    自动为失败的测试截图并附加到 Allure 报告
    """
    outcome = yield
    report = outcome.get_result()

    # 只在测试执行阶段且失败时处理
    if report.when == "call" and report.failed:
        driver = _find_available_driver(item)

        if driver:
            _capture_screenshot(driver, report)


def _find_available_driver(item):
    """查找可用的驱动实例"""
    # 单设备驱动检查
    single_driver_names = [
        "settings_driver", "ai_mate_driver", "dynamic_driver", "smart_driver"
    ]

    for driver_name in single_driver_names:
        driver = item.funcargs.get(driver_name)
        if driver and hasattr(driver, 'get_screenshot_as_png'):
            return driver

    # 多设备驱动检查
    multi_driver_names = [
        "multi_settings_drivers", "multi_ai_mate_drivers"
    ]

    for multi_driver_name in multi_driver_names:
        drivers = item.funcargs.get(multi_driver_name)
        if drivers and isinstance(drivers, dict) and drivers:
            # 返回第一个可用设备
            first_driver = next(iter(drivers.values()))
            if hasattr(first_driver, 'get_screenshot_as_png'):
                return first_driver

    return None


def _capture_screenshot(driver, report):
    """捕获并附加截图到测试报告"""
    try:
        # 验证驱动会话是否有效
        _ = driver.session_id

        screenshot_name = f"{report.nodeid}_{report.when}".replace("/", "_").replace("::", "_")
        screenshot_data = driver.get_screenshot_as_png()

        allure.attach(
            screenshot_data,
            name=screenshot_name,
            attachment_type=allure.attachment_type.PNG
        )

        print(f"📸 已为失败测试截图: {screenshot_name}")

    except Exception as error:
        print(f"⚠️ 截图失败: {error}")


# ==================== 测试配置和标记 ====================

def pytest_configure(config):
    """pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers",
        "multi_device: 标记需要多设备并行的测试"
    )
    config.addinivalue_line(
        "markers",
        "bluetooth_test: 标记蓝牙相关测试"
    )
    config.addinivalue_line(
        "markers",
        "settings_app: 标记设置应用测试"
    )
    config.addinivalue_line(
        "markers",
        "ai_mate_app: 标记 AI Mate 应用测试"
    )

# 删除或注释掉有问题的钩子函数
# def pytest_collection_modifyitems(config, items):
#     """测试收集修改钩子"""
#     # 可以根据需要添加测试排序或过滤逻辑
#     pass


# ==================== 可选 Fixtures ====================

# 如果需要向后兼容，可以取消注释以下 fixture
# 但注意：如果测试中没有使用它，仍然会产生警告

# @pytest.fixture(scope="function")
# def driver(ai_mate_driver):
#     """
#     兼容性 fixture - 默认使用 AI Mate 驱动
#     保持与现有测试用例的兼容性
#     """
#     return ai_mate_driver