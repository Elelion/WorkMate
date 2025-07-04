# установка / запуск тестов
pip install pytest pytest-cov <br>
pytest --cov=main tests/

# отчет по покрытию
coverage run -m pytest <br>
coverage report -m

# проверить help
python main.py --help

---

# Сделано
- Парсинг аргументов (parse_args) — есть
- Чтение CSV (read_csv) — есть
- Фильтрация (--where и функции parse_where_clause, filter_data) — есть
- Агрегация (--aggregate и функция apply_aggregation) — есть
- Выбор колонок (--select) — есть
- Группировка с агрегацией (--groupby + --aggregate + apply_group_by_aggregation) — есть
- Сортировка (--order-by + apply_sorting) — есть
- Вызов всего этого в main() с правильным порядком — есть
- Аннотации - есть

---

# Команды для запуска
- python main.py --file products.csv --where "price > 800"
- python main.py --file products.csv --where "price > 500" --aggregate "price=avg"
- python main.py --file products.csv --where "price > 500" --select name,price
- python main.py --file products.csv --groupby brand --aggregate price=avg
- python main.py --file products.csv --where "rating > 4.5" --order-by "rating=desc"
