import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate
import time
from tqdm import tqdm  # Для отображения прогресса

# Вывод приветствия в красивом формате
print("╔════════════════════════════════════╗")
print("║ Чекер статистики:                  ║")
print("║ ┌────────────────────────────────┐ ║")
print("║ │ 1. Lombard - нативные поинты   │ ║")
print("║ │    (прямой занос / LBTC Pende) │ ║")
print("║ │ 2. Lombard - pendle EtherFi    │ ║")
print("║ │ 3. Babylon - pendle EtherFi    │ ║")
print("║ └────────────────────────────────┘ ║")
print("║ Автор: KOTOV INVEST                ║")
print("╚════════════════════════════════════╝")

# Функция для получения данных по API с использованием прокси
def get_data_with_proxy(url, proxy):
    try:
        # Формируем прокси в формате, который понимает requests
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(url, proxies=proxy_dict, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

# Функция для получения значения Total из первого API
def get_total_from_first_api(address, proxy_list, max_retries=3):
    url = f"https://mainnet.prod.lombard.finance/api/v1/referral-system/season-1/points/{address}"
    for attempt in range(max_retries):
        proxy = proxy_list[attempt % len(proxy_list)]  # Берём новый прокси при каждой попытке
        data = get_data_with_proxy(url, proxy)
        if data and "total" in data:
            return data["total"]
        time.sleep(1)  # Задержка между попытками
    return 0

# Функция для получения значений Total Points для LOMBARD и BABYLON из второго API
def get_total_points(address, proxy_list, max_retries=3):
    url = f"https://app.ether.fi/api/portfolio/v3/{address}"
    for attempt in range(max_retries):
        proxy = proxy_list[attempt % len(proxy_list)]  # Берём новый прокси при каждой попытке
        data = get_data_with_proxy(url, proxy)
        if data and "totalPointsSummaries" in data:
            lombard_points = data["totalPointsSummaries"].get("LOMBARD", {}).get("TotalPoints", 0)
            babylon_points = data["totalPointsSummaries"].get("BABYLON", {}).get("TotalPoints", 0)
            return lombard_points, babylon_points
        time.sleep(1)  # Задержка между попытками
    return 0, 0

# Функция для обработки одного адреса
def process_address(address, proxy_list):
    total = get_total_from_first_api(address, proxy_list)
    lombard_total_points, babylon_total_points = get_total_points(address, proxy_list)
    return {
        "address": address,
        "Lombard Points Native": total,
        "Lombard Points EtherFi": lombard_total_points,
        "Babylon Points EtherFi": babylon_total_points
    }

# Основная функция
def main():
    # Чтение адресов из файла
    try:
        with open("wallets.txt", "r") as file:
            addresses = file.read().splitlines()
    except FileNotFoundError:
        print("Файл wallets.txt не найден.")
        return

    # Чтение прокси из файла
    try:
        with open("proxy.txt", "r") as file:
            proxies = file.read().splitlines()
    except FileNotFoundError:
        print("Файл proxy.txt не найден.")
        return

    if not proxies:
        print("Список прокси пуст. Проверьте файл proxy.txt.")
        return

    # Создание списка для сохранения результатов в правильном порядке
    results = [None] * len(addresses)

    # Обработка адресов в несколько потоков с отображением прогресса
    with ThreadPoolExecutor(max_workers=5) as executor:  # Уменьшили количество потоков до 5
        futures = []
        for i, address in enumerate(addresses):
            # Передаём также индекс адреса для сохранения порядка
            futures.append(executor.submit(lambda idx, addr: (idx, process_address(addr, proxies)), i, address))

        # Используем tqdm для отображения прогресса
        for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка адресов", unit="адрес"):
            try:
                idx, result = future.result()
                results[idx] = result  # Сохраняем результат по индексу
            except Exception:
                pass  # Игнорируем ошибки

            time.sleep(0.5)  # Задержка между обработкой адресов

    # Формируем таблицу для вывода в правильном порядке
    log_table = []
    for result in results:
        log_table.append([
            result['address'],
            result['Lombard Points Native'],
            result['Lombard Points EtherFi'],
            result['Babylon Points EtherFi']
        ])

    # Выводим красивые логи в реальном времени
    print("\n" + tabulate(log_table, headers=["Address", "Lombard Native", "Lombard EtherFi", "Babylon EtherFi"], tablefmt="pretty"))

    # Сохранение результатов в Excel
    try:
        df = pd.DataFrame(results)
        df.to_excel("results.xlsx", index=False)
        print("Результаты успешно сохранены в файл results.xlsx")
    except Exception:
        print("Ошибка при сохранении результатов в Excel.")

if __name__ == "__main__":
    main()