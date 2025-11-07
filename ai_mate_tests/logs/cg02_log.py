import serial
import threading
import datetime
import os

# 日志保存目录
LOG_DIR = r"C:\Users\536131\Desktop\workfile\CG02_眼镜\logs"

# 确保目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def log_serial(port, name):
    """监听串口并写入日志"""
    # 文件名包含日期+时分秒
    datetime_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"{name}_{datetime_str}.log")

    try:
        ser = serial.Serial(port, baudrate=2000000, timeout=1)  # 波特率 2000000
        print(f"✅ 开始监听 {port} ({name})，日志保存到 {log_file}")

        with open(log_file, "a", encoding="utf-8") as f:
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
                    log_line = f"{timestamp} {line}"
                    print(f"{name}: {log_line}")
                    f.write(log_line + "\n")
                    f.flush()

    except Exception as e:
        print(f"❌ 打开 {port} ({name}) 失败: {e}")

if __name__ == "__main__":
    # 开两个线程分别监听 COM12 和 COM13
    t1 = threading.Thread(target=log_serial, args=("COM12", "left_leg"))
    t2 = threading.Thread(target=log_serial, args=("COM11", "right_leg"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
