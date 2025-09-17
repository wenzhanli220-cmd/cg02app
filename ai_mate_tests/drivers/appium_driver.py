from appium import webdriver
from appium.options.android import UiAutomator2Options

def get_driver():
    options = UiAutomator2Options()

    # 基础配置
    options.platform_name = "Android"
    options.platform_version = "15"  
    options.device_name = "13826704BL00043"

    # 启动目标应用
    options.app_package = "com.transsion.xsound"
    options.app_activity = "com.transsion.xsound.MainActivity"

    # 优化参数
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.full_reset = False
    options.new_command_timeout = 300
    options.auto_grant_permissions = True
    options.unicode_keyboard = True
    options.reset_keyboard = True

    driver = webdriver.Remote("http://localhost:4723/wd/hub", options=options)
    driver.implicitly_wait(10)  # 全局隐式等待
    return driver
