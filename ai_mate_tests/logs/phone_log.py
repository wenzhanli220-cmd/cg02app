import subprocess
import time
import os
from datetime import datetime
import argparse

# 固定日志保存路径（你指定的目录）
LOG_SAVE_DIR = r"C:\Users\536131\Desktop\workfile\CG02_眼镜\phone_logs"


def ensure_dir_exists(path: str) -> None:
    """确保保存日志的目录存在，不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"📂 日志目录不存在，已自动创建：{path}")


def capture_phone_log(
        save_to_file: bool = True,  # 默认自动保存
        filter_keyword: str = None,
        stop_after_seconds: int = None
) -> None:
    """
    抓取手机 Log 并保存到指定目录
    :param save_to_file: 是否保存到文件（默认 True）
    :param filter_keyword: 过滤关键词（如 "Bluetooth"）
    :param stop_after_seconds: 抓取时长（秒，None 表示持续抓取）
    """
    # 确保保存目录存在
    ensure_dir_exists(LOG_SAVE_DIR)

    # 1. 构建 adb logcat 命令（带时间戳）
    adb_cmd = ["adb", "logcat", "-v", "time"]  # -v time 显示日志时间

    # 2. 添加关键词过滤（可选）
    if filter_keyword:
        adb_cmd.append(f"*{filter_keyword}*")
        print(f"🔍 过滤关键词：{filter_keyword}")

    # 3. 生成日志文件名（带时间戳，避免重复）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"phone_log_{timestamp}.txt"
    log_file_path = os.path.join(LOG_SAVE_DIR, log_filename)

    log_file = None
    if save_to_file:
        print(f"✅ 日志将保存到：{log_file_path}")

    try:
        # 启动 adb 进程抓取日志
        print(f"📱 开始抓取手机日志（按 Ctrl+C 停止）")
        process = subprocess.Popen(
            adb_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore"  # 忽略无法解码的字符
        )

        # 控制抓取时长
        start_time = time.time()
        while True:
            log_line = process.stdout.readline()
            if not log_line:
                break  # 进程结束时退出

            # 打印到控制台
            print(log_line.strip())

            # 保存到文件
            if save_to_file:
                if not log_file:
                    log_file = open(log_file_path, "a", encoding="utf-8", errors="ignore")
                log_file.write(log_line)
                log_file.flush()  # 实时写入，避免丢失

            # 检查是否达到指定时长
            if stop_after_seconds and (time.time() - start_time) >= stop_after_seconds:
                print(f"\n⏰ 已达到抓取时长（{stop_after_seconds} 秒），停止抓取")
                break

    except KeyboardInterrupt:
        print(f"\n🛑 用户手动停止抓取")
    except Exception as e:
        print(f"\n❌ 抓取失败：{str(e)}")
    finally:
        # 清理资源
        if log_file:
            log_file.close()
            print(f"\n📁 日志已保存：{log_file_path}")
        if process and process.poll() is None:
            process.terminate()


if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description="手机日志抓取工具（默认保存到指定目录）")
    parser.add_argument(
        "-k", "--keyword", type=str, help="过滤关键词（如 Bluetooth，默认抓取所有日志）"
    )
    parser.add_argument(
        "-t", "--time", type=int, help="抓取时长（秒，默认持续抓取直到 Ctrl+C）"
    )

    args = parser.parse_args()

    # 调用函数
    capture_phone_log(
        filter_keyword=args.keyword,
        stop_after_seconds=args.time
    )