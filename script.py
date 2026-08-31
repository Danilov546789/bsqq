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
        cfg_lower = cfg.lower()
        
        # Проверяем только наличие нужной страны в ссылке
        if any(country in cfg_lower for country in TARGET_COUNTRIES):
            filtered_configs.append(cfg)
                
    print(f"Найдено в сумме {len(filtered_configs)} серверов для выбранных регионов.")

    if not filtered_configs:
        print(f"В исходном файле не найдено серверов для стран: {', '.join(TARGET_COUNTRIES)}")
        return

    # Надежная сортировка
    filtered_configs.sort()

    # Извлекаем нужное количество серверов
    top_servers = filtered_configs[:MAX_GOOD_SERVERS]
    
    # Объединяем их в обычный текст через перенос строки
    final_text = "\n".join(top_servers)
    
    # Записываем результат в ваш файл vlessbs в чистом текстовом виде
    with open("vlessbs", "w", encoding="utf-8") as f:
        f.write(final_text)
        
    print(f"Успешно! Сохранено {len(top_servers)} текстовых серверов в файл vlessbs")

if __name__ == "__main__":
    main()
