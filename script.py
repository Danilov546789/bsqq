import requests
import base64
import time
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# ССЫЛКА НА ИСХОДНЫЙ ФАЙЛ (Укажите вашу ссылку, где 200+ серверов)
SOURCE_URL = "https://raw.githubusercontent.com/zieng2/wl/refs/heads/main/vless_universal.txt" 

# НАСТРОЙКИ ФИЛЬТРАЦИИ И ОТБОРА
TARGET_COUNTRY = "Netherlands"  # Какую страну оставить? (Например: Poland, Germany, Netherlands)
MAX_GOOD_SERVERS = 5        # Сколько лучших серверов этой страны оставить в подписке
TIMEOUT = 3                 # Секунды на ожидание ответа от сервера

def get_raw_configs():
    try:
        res = requests.get(SOURCE_URL, timeout=10)
        content = res.text
        # Декодируем base64, если исходный файл зашифрован
        if "://" not in content[:20]:
            content = base64.b64decode(content).decode('utf-8', errors='ignore')
        
        # Находим все конфигурации
        configs = re.findall(r'(vless://\S+|vmess://\S+|ss://\S+|trojan://\S+|shadowsocks://\S+)', content)
        return list(set(configs))  # Убираем дубликаты
    except Exception as e:
        print(f"Не удалось скачать базу: {e}")
        return []

def ping_server(config):
    """ Проверка доступности сервера через сокет """
    try:
        # Извлекаем host и port
        match = re.search(r'@([^:/\s]+):(\d+)', config)
        if not match:
            return None
        
        host, port = match.group(1), int(match.group(2))
        
        start_time = time.time()
        with socket.create_connection((host, port), timeout=TIMEOUT):
            latency = round((time.time() - start_time) * 1000)
            return {"config": config, "latency": latency}
    except:
        return None

def main():
    print("Скачиваем исходную базу серверов...")
    all_configs = get_raw_configs()
    
    if not all_configs:
        print("Список серверов пуст.")
        return

    print(f"Успешно загружено {len(all_configs)} конфигураций.")
    
    # ФИЛЬТРАЦИЯ ПО СТРАНЕ
    # Оставляем только те строки, где в названии (после #) есть нужное слово
    print(f"Фильтруем сервера по стране: {TARGET_COUNTRY}...")
    filtered_configs = []
    for cfg in all_configs:
        # Разбиваем строку по знаку #, чтобы проверить только имя сервера
        if '#' in cfg:
            name_part = cfg.split('#')[1]
            # Проверяем наличие страны (без учета регистра букв)
            if TARGET_COUNTRY.lower() in name_part.lower():
                filtered_configs.append(cfg)
                
    print(f"Найдено {len(filtered_configs)} серверов, подходящих под регион {TARGET_COUNTRY}.")

    if not filtered_configs:
        print(f"В исходном файле не найдено ни одного сервера для страны: {TARGET_COUNTRY}")
        return

    print("Запускаем отбор самых быстрых из них...")
    good_servers = []
    # Параллельно пингуем только отфильтрованные по стране сервера
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(ping_server, filtered_configs)
        for res in results:
            if res:
                good_servers.append(res)
                
    if not good_servers:
        print("Ни один из выбранных серверов не ответил на пинг.")
        return

    # Сортируем по пингу (от быстрых к медленным)
    good_servers.sort(key=lambda x: x['latency'])
    
    # Берем топ-5 лучших серверов выбранной страны
    top_servers = [item['config'] for item in good_servers[:MAX_GOOD_SERVERS]]
    
    # Собираем результат и кодируем в Base64
    final_text = "\n".join(top_servers)
    b64_output = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    
    # Сохраняем в файл подписки
    with open("vlessbs", "w") as f:
        f.write(b64_output)
        
    print(f"Успешно! Сохранено {len(top_servers)} лучших серверов для региона {TARGET_COUNTRY} в sub.txt")

if __name__ == "__main__":
    main()

