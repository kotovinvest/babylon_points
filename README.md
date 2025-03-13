# **Чекер статистики: Lombard и Babylon**

Программа предназначена для проверки статистики по адресам кошельков в системах **Lombard** и **Babylon**. Она собирает данные о поинтах (баллах) из различных API и сохраняет результаты в Excel-файл.

---

## **Основной функционал**
1. **Сбор данных о поинтах:**
   - Lombard Native Points (прямой занос / LBTC Pende).
   - Lombard Points через EtherFi.
   - Babylon Points через EtherFi.

2. **Поддержка прокси:**
   - формат log:pass@ip:port

3. **Сохранение результатов:**
   - Все собранные данные сохраняются в файл `results.xlsx` в формате таблицы и в логах терминала:
**Таблица в терминале**
+------------------+----------------+------------------+--------------------+
| Address          | Lombard Native | Lombard EtherFi  | Babylon EtherFi   |
+------------------+----------------+------------------+--------------------+
| 0x123...         | 100            | 200              | 150                |
| 0x456...         | 50             | 0                | 300                |
+------------------+----------------+------------------+--------------------+

---

## **Установка и запуск**

pip install -r requirements.txt
py main.py

## **Telegram: @kotov_invest**
