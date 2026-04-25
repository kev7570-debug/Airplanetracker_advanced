"""Модуль для чтения конфигурации базы данных."""

from configparser import ConfigParser
from typing import Dict


def config(filename: str = "database.ini", section: str = "postgresql") -> Dict[str, str]:
    """Чтение конфигурации PostgreSQL из файла.

    Args:
        filename: Имя файла конфигурации
        section: Секция в файле конфигурации

    Returns:
        Dict[str, str]: Параметры подключения к БД

    Raises:
        Exception: Если секция не найдена
    """
    parser = ConfigParser()
    parser.read(filename)

    db_params = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db_params[param[0]] = param[1]
    else:
        raise Exception(f"Секция {section} не найдена в файле {filename}")

    return db_params
