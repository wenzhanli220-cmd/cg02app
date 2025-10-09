# ai_mate_tests/utils/config.py

# Appium 服务地址
APPIUM_SERVER_URL = "http://localhost:4723/wd/hub"


# 设备配置
DEVICE_CONFIG = {
    "platformName": "Android",
    "platformVersion": "15",   # 根据你设备系统版本填写
    "deviceName": "11467253AU000413",
    "automationName": "UiAutomator2"
}

APP_CONFIGS = {
    "ai_mate": {
        "appPackage": "com.transsion.xsound",
        "appActivity": "com.transsion.xsound.MainActivity"
    },
    "settings": {
        "appPackage": "com.android.settings",
        "appActivity": "com.android.settings.Settings"
    }
}

# 其他 driver 配置
DRIVER_OPTIONS = {
    "noReset": True,
    "fullReset": False,
    "newCommandTimeout": 300,
    "autoGrantPermissions": True,
    "unicodeKeyboard": True,
    "resetKeyboard": True
}
