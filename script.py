import requests
import base64
import re

# ССЫЛКА НА ИСХОДНЫЙ ФАЙЛ
SOURCE_URL = "https://githubusercontent.com" 

# НАСТРОЙКИ ФИЛЬТРАЦИИ И ОТБОРА
TARGET_COUNTRIES = ["netherlands", "germany", "finland"] 
MAX_GOOD_SERVERS = 30            # Сколько серверов оставить в подписке

def get_raw_configs():
    try:
        res = requests.get(SOURCE_URL, timeout=10)
        content = res.text
        if "://" not in content[:20]:
            content = base64.b64decode(content).decode('utf-8', errors='ignore')
        
        configs = re.findall(r'(vless://\S+|vmess://\S+|ss://\S+|trojan://\S+|shadowsocks://\S+)', content)
        return list(set(configs))  # Убираем дубликаты
    except Exception as e:
        print(f"Не удалось скачать базу: {e}")
        return []

def main():
    print("Скачиваем исходную базу серверов...")
    all_configs = get_raw_configs()
    
    if not all_configs:
        print("Список серверов пуст.")
        return

    print(f"Успешно загружено {len(all_configs)} конфигураций.")
    print(f"Фильтруем сервера по странам: {', '.join(TARGET_COUNTRIES)}...")
    
    filtered_configs = []
    for cfg in all_configs:
        if '#' in cfg:
            # Безопасно делим строку по знаку решетки
            parts = cfg.split('#', 1)
            # Берем строго вторую часть (текстовое имя после #) и приводим к маленьким буквам
            name_part = parts[1].lower()
            cfg_lower = cfg.lower()
            
            # Фильтр по странам + защита от неподходящих под БС протоколов (Reality/gRPC)
            if any(country in name_part for country in TARGET_COUNTRIES):
                if "reality" not in cfg_lower and "grpc" not in cfg_lower:
                    filtered_configs.append(cfg)
                
    print(f"Найдено в сумме {len(filtered_configs)} серверов для выбранных регионов.")

    if not filtered_configs:
        print(f"В исходном файле не найдено серверов для стран: {', '.join(TARGET_COUNTRIES)}")
        return

    # Безопасная сортировка: временно создаем пары (имя_сервера, вся_ссылка),
    # сортируем их по имени, а потом забираем обратно чистые ссылки.
    temp_list = []
    for cfg in filtered_configs:
        parts = cfg.split('#', 1)
        name_for_sort = parts[1].lower() if len(parts) > 1 else cfg.lower()
        temp_list.append((name_for_sort, cfg))
    
    # Сортируем по первому элементу (красивому имени после #)
    temp_list.sort(key=lambda item: item[0])
    
    # Собираем обратно отсортированный список ссылок
    sorted_configs = [item[1] for item in temp_list]

    # Берем нужное количество упорядоченных серверов (до 30 штук)
    top_servers = sorted_configs[:MAX_GOOD_SERVERS]
    
    # Объединяем их в обычный текст, где каждый сервер с новой строки
    final_text = "\n".join(top_servers)
    
    # Сохраняем в ваш файл vlessbs в чистом текстовом виде БЕЗ Base64
    with open("vlessbs", "w", encoding="utf-8") as f:
        f.write(final_text)
        
    print(f"Успешно! Сохранено {len(top_servers)} упорядоченных текстовых серверов в файл vlessbs")

if __name__ == "__main__":
    main()
