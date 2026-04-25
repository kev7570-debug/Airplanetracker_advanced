"""Модуль для создания базы данных и таблиц."""

from typing import Dict

import psycopg2


def create_database(db_name: str, params: Dict[str, str]) -> None:
    """Создание базы данных.

    Args:
        db_name: Имя создаваемой базы данных
        params: Параметры подключения к PostgreSQL
    """
    # Подключаемся к стандартной базе postgres
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()

    # Проверяем, существует ли БД
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"База данных '{db_name}' создана")
    else:
        print(f"База данных '{db_name}' уже существует")

    cur.close()
    conn.close()


def create_tables(db_name: str, params: Dict[str, str]) -> None:
    """Создание таблиц countries и aeroplanes с FK связью.

    Args:
        db_name: Имя базы данных
        params: Параметры подключения к PostgreSQL
    """
    # Подключаемся к созданной БД
    params.update({'dbname': db_name})
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # Создание таблицы countries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            country_name VARCHAR(100) UNIQUE NOT NULL,
            lamin FLOAT,
            lamax FLOAT,
            lomin FLOAT,
            lomax FLOAT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Создание таблицы aeroplanes с FK на countries
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aeroplanes (
            id SERIAL PRIMARY KEY,
            icao24 VARCHAR(10) NOT NULL,
            callsign VARCHAR(20),
            registration_country VARCHAR(100) NOT NULL,
            velocity FLOAT,
            altitude FLOAT,
            latitude FLOAT,
            longitude FLOAT,
            on_ground BOOLEAN DEFAULT FALSE,
            country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(icao24, created_at)
        )
    """)

    conn.commit()
    print("Таблицы 'countries' и 'aeroplanes' созданы")

    cur.close()
    conn.close()
