import argparse
import csv
import operator
import statistics
from typing import Any, Optional

from color_console import *
from tabulate import tabulate


operations:dict[str, Any] = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

agg_funcs:dict[str, Any] = {
    'sum': sum,
    'avg': statistics.mean,
    'min': min,
    'max': max,
    'count': len,
}


# -----------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """
    Шаг 1: Парсинг аргументов командной строки

    :return объект с аргументами
    """

    parser = argparse.ArgumentParser(description="CSV фильтрация и агрегация")

    parser.add_argument("--file", required=True, help="Путь к CSV файлу")
    parser.add_argument("--where", help="Фильтр по условию (пример: rating>4.7)")
    parser.add_argument("--aggregate", help="Агрегация (пример: price=avg)")
    parser.add_argument("--select", help="Вывести только указанные поля (пример: name,price)")
    parser.add_argument("--groupby", help="Группировка по полю (пример: brand)")
    parser.add_argument("--order-by", help="Сортировка: поле=asc|desc (пример: price=asc или rating=desc)")

    return parser.parse_args()

def read_csv(file_path:str) -> list[dict[str, Any]]:
    """
    Шаг 2 — Чтение CSV и вывод всех строк
    """

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


# **


def parse_where_filter(where_op:str) -> tuple[str, Any, str]:
    """
    Шаг 3 — Фильтрация по --where
    """

    for operation in sorted(operations.keys(), key=len, reverse=True):  # сначала >=, <=, потом >, <
        if operation in where_op :
            op_field, op_value = where_op .split(operation)
            return op_field.strip(), operations[operation], op_value.strip()
    raise ValueError("Неправильный формат условия. Пример: price > 100")

def filter_data(rows:list[dict[str, str]], where_filter:str) -> list[dict[str, str]]:
    """
    Шаг 3 — для main и тестов
    """

    field, op_func, value = parse_where_filter(where_filter)

    # Преобразование value
    if value.replace(".", "", 1).isdigit():
        value = float(value) if '.' in value else int(value)

    # Фильтрация
    return [
        row for row in rows if field in row and op_func(
            float(row[field]) if '.' in row[field] or isinstance(value, float) else int(row[field]),
            value
        )
    ]


# **


def apply_aggregation(agg_rows:list, agg_str:str) -> Optional[None]:
    """
    Шаг 4 — Агрегация по полю
    Пример: price=avg
    """

    agg_field, agg_func_name = agg_str.split("=")
    agg_field = agg_field.strip()
    agg_func_name = agg_func_name.strip().lower()

    values = []

    for row in agg_rows:
        if agg_field in row:
            try:
                values.append(float(row[agg_field]))
            except ValueError:
                pass  # Пропускаем строки с нечисловыми значениями

    if not values:
        print_subtitle("Нет данных для агрегации")
        return

    if agg_func_name == "sum":
        result = sum(values)
    elif agg_func_name == "avg":
        result = sum(values) / len(values)
    elif agg_func_name == "min":
        result = min(values)
    elif agg_func_name == "max":
        result = max(values)
    elif agg_func_name == "count":
        result = len(values)
    else:
        print_subtitle("Неподдерживаемая функция агрегации:", agg_func_name)
        return

    print_subtitle(f"\nРезультат агрегации: {agg_func_name.upper()}({agg_field}) = {result}")


# **


def parse_aggregate_clause(agg_str:str) -> tuple[str, str]:
    """
    Шаг 6 — добавим поддержку --groupby
    Разбирает агрегат: price=avg -> ('price', 'avg')
    """

    if '=' not in agg_str:
        raise ValueError("Неправильный формат агрегата. Пример: price=avg")

    field, func = agg_str.split('=')
    return field.strip(), func.strip().lower()

def apply_group_by_aggregation(rows:list, group_by:str, aggregate:str) -> dict[str, Any]:
    """
    Шаг 6 — для main и тестов
    """

    group_field = group_by
    agg_field, agg_func_name = parse_aggregate_clause(aggregate)

    if agg_func_name not in agg_funcs:
        raise ValueError(f"Неизвестная агрегатная функция: {agg_func_name}")

    grouped = {}
    for row in rows:
        key = row[group_field]
        val = float(row[agg_field])
        grouped.setdefault(key, []).append(val)

    print_subtitle(f"\nГруппировка по '{group_field}', агрегат {agg_func_name} по '{agg_field}':")

    results = {}
    for key, values in grouped.items():
        result = agg_funcs[agg_func_name](values)
        print_subtitle(f"{key}: {result}")
        results[key] = result

    return results


# **


def parse_order_by_clause(order_str:str) -> tuple[str, str]:
    """
    Шаг 7 — добавим --order-by
    """

    if '=' not in order_str:
        raise ValueError("Формат сортировки должен быть: поле=asc|desc")

    field, direction = order_str.split('=')
    direction = direction.strip().lower()

    if direction not in ("asc", "desc"):
        raise ValueError("Сортировка может быть только asc или desc")
    return field.strip(), direction

def apply_sorting(sorting_rows:list[dict[str, str]], order_by:str) -> None:
    """
    Шаг 7 — для main и тестов
    desk - задается явно
    asc - по умолчанию
    """

    order_field, order_direction = parse_order_by_clause(order_by)

    def try_float(val):
        """
        Пробуем преобразовать val в float для корректной сортировки
        те '4.6' -> 4.6
        """

        try:
            return float(val)
        except (ValueError, TypeError):
            return val

    sorting_rows.sort(
        key=lambda row: try_float(row[order_field]),
        reverse=(order_direction == "desc")
    )


# -----------------------------------------------------------------------------


def main():
    args = parse_args()  # шаг 1
    rows = read_csv(args.file)  # шаг 2

    # **

    print_title("Путь к файлу:", args.file)
    if args.where:
        print("Фильтр:", args.where)
    if args.aggregate:
        print("Агрегация:", args.aggregate)

    # **
    # шаг 3
    # python main.py --file products.csv --where "price > 800"

    if args.where:
        rows = filter_data(rows, args.where)

    # **
    # шаг 7
    # важно! должна идти ПЕРЕД агрегатами и сортировкой
    # python main.py --file products.csv --where "rating > 4.5" --order-by "rating=desc"

    if args.order_by:
        apply_sorting(rows, args.order_by)

    # **

    print_title("\nСодержимое CSV:")
    print(tabulate(rows, headers="keys", tablefmt="grid"))

    # **
    # шаг 4
    # python main.py --file products.csv --where "price > 500" --aggregate "price=avg"

    if args.aggregate:
        apply_aggregation(rows, args.aggregate)

    # **
    # шаг 5
    # python main.py --file products.csv --where "price > 500" --select name,price

    if args.select:
        selected_fields = [field.strip() for field in args.select.split(",")]
        print_title(f"\nВывод только полей: {selected_fields}")

        filtered_rows = [
            {field: row[field] for field in selected_fields if field in row}
            for row in rows
        ]

        print(tabulate(filtered_rows, headers="keys", tablefmt="grid"))
    else:
        print_title("\nРезультат:")
        print(tabulate(rows, headers="keys", tablefmt="grid"))

    # **
    # шаг 6
    # python main.py --file products.csv --groupby brand --aggregate price=avg

    if args.groupby and args.aggregate:
        apply_group_by_aggregation(rows, args.groupby, args.aggregate)


if __name__ == "__main__":
    main()
