# -------------------------------
# 一键执行 pytest + allure 报告
# 保存文件名：run_tests.ps1
# -------------------------------

# 1. 运行 pytest，生成 allure-results
Write-Host "▶️ 开始运行测试..."
pytest --alluredir=allure-results

if (-Not (Test-Path "allure-results")) {
    Write-Host "❌ 测试运行失败，未生成 allure-results"
    exit 1
}

# 2. 生成 allure-report
Write-Host "📊 生成 Allure 报告..."
allure generate allure-results -o allure-report --clean

if (-Not (Test-Path "allure-report")) {
    Write-Host "❌ 报告生成失败"
    exit 1
}

# 3. 打包 allure-report 到 zip
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "allure-report-$timestamp.zip"

Write-Host "📦 正在打包报告到 $zipName ..."
Compress-Archive -Path "allure-report\*" -DestinationPath $zipName -Force

Write-Host "🎉 全流程完成！"
Write-Host "报告路径：allure-report\index.html"
Write-Host "压缩包：$zipName"
