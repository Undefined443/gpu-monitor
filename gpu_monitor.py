import os
import time
import socket
import signal
import sys
import requests
import logging
import GPUtil
from dotenv import load_dotenv

load_dotenv()
INTERVAL = 2
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def get_gpu_usage_gputil():
    try:
        gpus = GPUtil.getGPUs()
        gpu_usage = []
        for gpu in gpus:
            gpu_usage.append({
                "gpu_id": gpu.id,
                "memory_used": gpu.memoryUsed,
                "memory_total": gpu.memoryTotal,
                "util": gpu.load,
            })
        return gpu_usage
    except Exception as e:
        return f"Error using GPUtil: {e}"


def send_message(message: str):
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    assert message is not None
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    proxies = {"https": os.getenv("https_proxy")}
    response = requests.post(url, json=payload, proxies=proxies)
    if not response.ok:
        print("Send failed: ", response.text)


def find_idle_gpu():
    usage = get_gpu_usage_gputil()
    for gpu in usage:
        if gpu["memory_used"] < 1024 and gpu["util"] < 5:
            yield gpu


def signal_handler(sig, frame):
    print("\nCtrl+C entered, exiting...")
    sys.exit(0)


def main():
    hostname = socket.gethostname()
    while True:
        logging.info("Finding idle gpus...")
        for gpu in find_idle_gpu():
            memory_used = gpu["memory_used"] / 1024
            memory_total = gpu["memory_total"] / 1024
            util = gpu["util"] * 100
            message = f"Host: {hostname}\nGPU: {gpu['gpu_id']}\nMemory Used: {memory_used:.2f} GiB / {memory_total:.2f} GiB\nGPU Utilization: {util:.0f}%"
            send_message(message)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
