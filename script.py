import requests
import base64
import re

# ССЫЛКА НА ИСХОДНЫЙ ФАЙЛ
SOURCE_URL = "https://raw.githubusercontent.com/zieng2/wl/refs/heads/main/vless_universal.txt" 

# НАСТРОЙКИ ФИЛЬТРАЦИИ И ОТБОРА
# 1. ИЗМЕНЕНО: Заменили одну строку на список стран (пишите строго маленькими буквами в кавычках через запятую)
TARGET_COUNTRIES = ["netherlands", "germany", "finland"] 
MAX_GOOD_SERVERS = 20            # Сколько серверов оставить в подписке

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
    # 2. ИЗМЕНЕНО: Красивый вывод списка стран в логи
    print(f"Фильтруем сервера по странам: {', '.join(TARGET_COUNTRIES)}...")
    
    filtered_configs = []
    for cfg in all_configs:
        if '#' in cfg:
            name_part = cfg.split('#')[1]
            # 3. ИЗМЕНЕНО: Проверяем, есть ли хотя бы одна страна из нашего списка в названии сервера
            if any(country in name_part.lower() for country in TARGET_COUNTRIES):
                filtered_configs.append(cfg)
                
    # 4. ИЗМЕНЕНО: Скорректирован текст логов для нескольких стран
    print(f"Найдено в сумме {len(filtered_configs)} серверов для выбранных регионов.")

    if not filtered_configs:
        print(f"В исходном файле не найдено серверов для стран: {', '.join(TARGET_COUNTRIES)}")
        return

    # Берем нужное количество серверов
    top_servers = filtered_configs[:MAX_GOOD_SERVERS]
    
    # Объединяем их в обычный текст, где каждый сервер с новой строки
    final_text = "\n".join(top_servers)
    
    # Сохраняем в ваш файл vlessbs в чистом текстовом виде БЕЗ Base64
    with open("vlessbs", "w", encoding="utf-8") as f:
        f.write(final_text)
        
    print(f"Успешно! Сохранено {len(top_servers)} свежих текстовых серверов в файл vlessbs")

if __name__ == "__main__":
    main()
