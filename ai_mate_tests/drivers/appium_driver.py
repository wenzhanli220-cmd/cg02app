from appium import webdriver
from appium.options.android import UiAutomator2Options
from ai_mate_tests.utils.config import APPIUM_SERVER_URL, DEVICE_CONFIG, APP_CONFIGS, DRIVER_OPTIONS

def get_driver(app_name="ai_mate"):
    """
    获取 driver
    :param app_name: "ai_mate" 或 "settings"
    """
    options = UiAutomator2Options()

    # 基础配置
    options.platform_name = DEVICE_CONFIG["platformName"]
    options.platform_version = DEVICE_CONFIG["platformVersion"]
    options.device_name = DEVICE_CONFIG["deviceName"]
    options.automation_name = DEVICE_CONFIG["automationName"]

    # 选择启动的 APP
    app_config = APP_CONFIGS[app_name]
    options.app_package = app_config["appPackage"]
    options.app_activity = app_config["appActivity"]

    # 其他配置
    for key, value in DRIVER_OPTIONS.items():
        setattr(options, key, value)

    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    driver.implicitly_wait(10)
    return driver
