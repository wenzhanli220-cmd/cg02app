import os
import subprocess
import zipfile
from datetime import datetime

def generate_and_zip_report():
    project_root = os.path.dirname(os.path.abspath(__file__))
    allure_results = os.path.join(project_root, "allure-results")
    allure_report = os.path.join(project_root, "allure-report")

    if not os.path.exists(allure_results):
        print("❌ 没有找到 allure-results 文件夹，请先运行 pytest 生成测试结果！")
        return

    # 1. 调用 allure 命令生成报告
    print("⚡ 正在生成 Allure 报告...")
    try:
        subprocess.run(
            ["allure", "generate", allure_results, "-o", allure_report, "--clean"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("❌ 生成 Allure 报告失败，请确认 allure 已正确安装！")
        return

    # 2. 打包 allure-report 为 zip
    zip_name = f"allure-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(project_root, zip_name)

    print(f"📦 正在打包报告到 {zip_path} ...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(allure_report):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, allure_report)
                zipf.write(file_path, arcname)

    print("✅ 报告生成并打包完成！")
    print(f"👉 发送这个文件给别人即可： {zip_path}")

if __name__ == "__main__":
    generate_and_zip_report()
