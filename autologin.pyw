import requests
import time
import socket
import subprocess
import platform
import datetime
import os

# ================= 配置区域 =================
BASE_URL = "http://172.16.253.3:801/eportal/"
ACCOUNT = "YourAccount"
PASSWORD = "PassWord"
TEST_HOST = "www.baidu.com"

# --- 日志配置 ---
# 指定日志文件夹路径
LOG_DIR = r"D:\Autologin"
# 指定日志文件全路径
LOG_FILE = os.path.join(LOG_DIR, "run_log.txt")

# 确保文件夹存在，如果不存在则自动创建
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception:
        # 如果D盘不存在或无法创建，回退到临时目录防止报错
        LOG_FILE = "run_log.txt" 
# ===========================================

def get_now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(content):
    """写日志到 D:\Autologin\run_log.txt"""
    msg = f"[{get_now_str()}] {content}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_internet():
    """Ping 检测 (宽松模式: 3次)"""
    system_type = platform.system().lower()
    if system_type == 'windows':
        command = ['ping', '-n', '3', '-w', '2000', TEST_HOST]
    else:
        command = ['ping', '-c', '3', '-W', '2', TEST_HOST]
    
    try:
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False

def login():
    current_ip = get_local_ip()
    log(f"发起登录请求... IP: {current_ip}")
    
    params = {
        'c': 'Portal', 'a': 'login', 'callback': 'dr1003',
        'login_method': '1', 'user_account': ACCOUNT, 'user_password': PASSWORD,
        'wlan_user_ip': current_ip, 'wlan_user_mac': '000000000000',
        'wlan_ac_ip': '172.16.253.1', 'jsVersion': '3.3.2', 'v': '971'
    }
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        requests.get(BASE_URL, params=params, headers=headers, timeout=10)
    except Exception as e:
        log(f"登录请求异常: {e}")

def main():
    # 开机启动缓冲
    time.sleep(30)
    log("=== 脚本启动 (日志路径: D:\\Autologin) ===")

    while True:
        # --- 阶段 1: 常规检测 ---
        if check_internet():
            # 网络通畅，静默休眠 30 分钟
            time.sleep(1800)
        else:
            # --- 阶段 2: 断网急救 ---
            log("网络断开！进入急救模式...")
            
            while True:
                login()
                time.sleep(5) # 等待网络生效
                
                if check_internet():
                    log("重连成功！恢复监控。")
                    break 
                else:
                    log("重连失败，1分钟后重试...")
                    time.sleep(60)

if __name__ == "__main__":
    main()