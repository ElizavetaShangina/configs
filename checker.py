import requests
import base64
import json
import socket
import time
from urllib.parse import urlparse


SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt" 
TIMEOUT = 2.0
TOP_N = 25

def get_ip_port(config):
    try:
        if config.startswith('vmess://'):
            b64_str = config[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            data = json.loads(base64.b64decode(b64_str).decode('utf-8', errors='ignore'))
            return data.get('add') or data.get('host'), int(data.get('port'))
        else:
            parsed = urlparse(config)
            return parsed.hostname, parsed.port
    except Exception:
        return None, None

def check_tcp_ping(ip, port):
    if not ip or not port:
        return -1
    start_time = time.time()
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            return round((time.time() - start_time) * 1000)
    except (socket.timeout, socket.error, ConnectionRefusedError):
        return -1

def main():
    print("Скачиваем исходные конфиги...")
    try:
        response = requests.get(SOURCE_URL, timeout=10)
        configs = response.text.splitlines()
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return

    working_configs = []
    print(f"Найдено {len(configs)} строк. Проверяем...")

    for config in configs:
        config = config.strip()
        if not config:
            continue
            
        ip, port = get_ip_port(config)
        ping = check_tcp_ping(ip, port)
        
        if ping != -1:
            working_configs.append({"config": config, "ping": ping})
    working_configs.sort(key=lambda x: x["ping"])
    best_configs = working_configs[:TOP_N]

    if not best_configs:
        print("К сожалению, рабочих серверов не найдено.")
        return

    raw_text = "\n".join([item['config'] for item in best_configs])
    encoded_text = base64.b64encode(raw_text.encode('utf-8')).decode('utf-8')
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write(encoded_text)
        
    print(f"Успешно сохранено {len(best_configs)} конфигов в файл sub.txt")

if __name__ == "__main__":
    main()
