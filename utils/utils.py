import json


def read_json(file) -> list:
    """Считывает файл json"""
    with open(file,  encoding="UTF-8") as f:
        data = json.load(f)
    return data


def get_employers(data: list) -> list:
    """Получает список кортежей из списка словарей"""
    employers = []
    for item in data:
        employers.append((item['id'], item['title']))
    return employers
