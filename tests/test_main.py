import pytest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import *
from main import filter_data
from unittest import mock


# **


def test_parse_args_basic():
    test_args = [
        "main.py",
        "--file", "products.csv",
        "--where", "price>100",
        "--aggregate", "price=avg",
        "--select", "name,price",
        "--groupby", "brand",
        "--order-by", "price=desc"
    ]
    with mock.patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.file == "products.csv"
        assert args.where == "price>100"
        assert args.aggregate == "price=avg"
        assert args.select == "name,price"
        assert args.groupby == "brand"
        assert args.order_by == "price=desc"

def test_read_csv():
    csv_content = "name,price\nA,100\nB,200\n"
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv", encoding="utf-8") as tmp:
        tmp.write(csv_content)
        tmp_path = tmp.name

    try:
        rows = read_csv(tmp_path)
        assert rows == [
            {"name": "A", "price": "100"},
            {"name": "B", "price": "200"},
        ]
    finally:
        os.remove(tmp_path)

def test_parse_where_clause():
    field, op_func, value = parse_where_clause("price>=100")
    assert field == "price"
    assert op_func == operations[">="]
    assert value == "100"

def test_invalid_where_clause():
    with pytest.raises(ValueError):
        parse_where_clause("invalid expression")

def test_filter_data():
    rows = [
        {"price": "50"},
        {"price": "100"},
        {"price": "200"},
        {"price": "300"},
        {"price": "400"},
        {"price": "500"},
        {"price": "600"},
        {"price": "700"},
    ]

    # берем только те строки из rows, где цена больше 100
    filtered = filter_data(rows, "price>100")

    # assert — специальное ключевое слово, которое проверяет,
    # что выражение справа от него истинно (True).
    assert filtered == [
        {"price": "200"},
        {"price": "300"},
        {"price": "400"},
        {"price": "500"},
        {"price": "600"},
        {"price": "700"},
    ]

def test_apply_aggregation_no_data(capsys):
    rows = [
        {"price": "abc"},
        {"price": "xyz"},
    ]
    apply_aggregation(rows, "price=sum")
    captured = capsys.readouterr()
    assert "Нет данных для агрегации" in captured.out

def test_apply_aggregation_unsupported_func(capsys):
    rows = [
        {"price": "10"},
        {"price": "20"},
    ]
    apply_aggregation(rows, "price=median")
    captured = capsys.readouterr()
    assert "Неподдерживаемая функция агрегации" in captured.out

def test_parse_aggregate_clause_valid():
    field, func = parse_aggregate_clause("price=avg")
    assert field == "price"
    assert func == "avg"

def test_parse_aggregate_clause_invalid():
    with pytest.raises(ValueError):
        parse_aggregate_clause("priceavg")

def test_apply_group_by_aggregation():
    rows = [
        {"brand": "Sony", "price": "100"},
        {"brand": "Sony", "price": "300"},
        {"brand": "LG", "price": "200"},
    ]

    result = apply_group_by_aggregation(rows, "brand", "price=avg")
    assert result == {"Sony": 200.0, "LG": 200.0}

def test_parse_order_by_clause_valid():
    field, direction = parse_order_by_clause("price=asc")
    assert field == "price"
    assert direction == "asc"

    field, direction = parse_order_by_clause("rating=desc")
    assert field == "rating"
    assert direction == "desc"

def test_parse_order_by_clause_invalid_format():
    import pytest
    with pytest.raises(ValueError):
        parse_order_by_clause("priceasc")

def test_parse_order_by_clause_invalid_direction():
    import pytest
    with pytest.raises(ValueError):
        parse_order_by_clause("price=up")

def test_apply_sorting():
    rows = [
        {"name": "A", "rating": "4.5"},
        {"name": "B", "rating": "4.9"},
        {"name": "C", "rating": "4.1"},
    ]

    # Сортировка по убыванию
    apply_sorting(rows, "rating=desc")
    assert [row["name"] for row in rows] == ["B", "A", "C"]

    # Сортировка по возрастанию
    apply_sorting(rows, "rating=asc")
    assert [row["name"] for row in rows] == ["C", "A", "B"]

def test_main_full_flow(monkeypatch, tmp_path, capsys):
    # Создаём временный CSV-файл
    test_file = tmp_path / "data.csv"
    test_file.write_text("name,price,brand\nTV,150,Sony\nPhone,50,LG\n")

    test_args = [
        "main.py",
        "--file", str(test_file),
        "--where", "price>100",
        "--aggregate", "price=avg",
        "--select", "name,price",
        "--groupby", "brand",
        "--order-by", "price=desc"
    ]

    monkeypatch.setattr(sys, "argv", test_args)
    main()

    captured = capsys.readouterr()
    assert "Sony" in captured.out
    assert "150" in captured.out
