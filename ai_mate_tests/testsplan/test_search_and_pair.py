from ai_mate_tests.pages.device_page import DevicePage
from ai_mate_tests.pages.welcome_page import WelcomePage






def test_search_and_pair(driver):
    welcome = WelcomePage(driver)
    device = DevicePage(driver)

    # Step 1: 同意协议、进入首页
    # welcome.accept_all()

    # Step 2: 点击搜索到的眼镜设备
    device.search_device()

    # Step 3: 点击配对
    device.pair_device()

    # Step 4: 断言：是否进入到含有 “对话翻译” 的页面
    assert device.is_paired_success(timeout=30), "❌ 配对失败，未检测到 '对话翻译' 页面"
    print("✅ 配对成功，进入 '对话翻译' 页面")
