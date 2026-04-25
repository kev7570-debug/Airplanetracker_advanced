"""Модуль для работы с базой данных (DBManager)."""

from typing import Any, Dict, List, Tuple

import psycopg2

from src.aeroplane_module import Aeroplane
from src.api_module import AeroplanesAPI


class DBManager:
    """Класс для управления данными в PostgreSQL."""

    def __init__(self, db_name: str, params: Dict[str, str]):
        """Инициализация DBManager.

        Args:
            db_name: Имя базы данных
            params: Параметры подключения к PostgreSQL
        """
        self.db_name = db_name
        self.params = params.copy()
        self.params.update({'dbname': db_name})

    def _get_connection(self):
        """Получение соединения с БД."""
        return psycopg2.connect(**self.params)

    def save_country_data(self, country: str, coordinates: Dict[str, float]) -> int:
        """Сохранение страны в БД.

        Args:
            country: Название страны
            coordinates: Координаты bounding box

        Returns:
            int: ID сохраненной страны
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO countries (country_name, lamin, lamax, lomin, lomax)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (country_name) DO UPDATE
                    SET lamin = EXCLUDED.lamin,
                        lamax = EXCLUDED.lamax,
                        lomin = EXCLUDED.lomin,
                        lomax = EXCLUDED.lomax,
                        last_updated = CURRENT_TIMESTAMP
                    RETURNING id
                """, (country, coordinates['lamin'], coordinates['lamax'],
                      coordinates['lomin'], coordinates['lomax']))

                return cur.fetchone()[0]

    def save_aeroplanes(self, country_id: int, aeroplanes: List[Aeroplane]) -> None:
        """Сохранение списка самолетов в БД.

        Args:
            country_id: ID страны (FK)
            aeroplanes: Список объектов Aeroplane
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                for plane in aeroplanes:
                    cur.execute("""
                        INSERT INTO aeroplanes
                        (icao24, callsign, registration_country, velocity,
                         altitude, latitude, longitude, on_ground, country_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (icao24, created_at) DO NOTHING
                    """, (plane.icao24, plane.callsign, plane.country,
                          plane.velocity, plane.altitude, plane.latitude,
                          plane.longitude, plane.on_ground, country_id))

    def get_info_countries_and_planes(self) -> List[Tuple[str, int]]:
        """Получает список всех стран и количество самолетов в каждой.

        Returns:
            List[Tuple[str, int]]: Список кортежей (страна, количество)
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.country_name, COUNT(a.id) as planes_count
                    FROM countries c
                    LEFT JOIN aeroplanes a ON c.id = a.country_id
                    GROUP BY c.country_name
                    ORDER BY planes_count DESC
                """)
                return cur.fetchall()

    def get_all_planes(self) -> List[Tuple[str, str, float, float]]:
        """Получает список всех самолетов с указанием страны регистрации.

        Returns:
            List[Tuple[str, str, float, float]]: (страна, позывной, скорость, высота)
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT registration_country, callsign, velocity, altitude
                    FROM aeroplanes
                    WHERE on_ground = false
                    ORDER BY altitude DESC
                """)
                return cur.fetchall()

    def get_avg_height(self) -> float:
        """Получает среднюю высоту полета всех самолетов.

        Returns:
            float: Средняя высота полета
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT AVG(altitude) FROM aeroplanes WHERE on_ground = false")
                result = cur.fetchone()[0]
                return float(result) if result else 0.0

    def get_max_height(self) -> List[Tuple[str, float, str]]:
        """Получает список самолетов, летящих выше средней высоты.

        Returns:
            List[Tuple[str, float, str]]: (позывной, высота, страна)
        """
        avg_height = self.get_avg_height()

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT callsign, altitude, registration_country
                    FROM aeroplanes
                    WHERE on_ground = false AND altitude > %s
                    ORDER BY altitude DESC
                """, (avg_height,))
                return cur.fetchall()

    def get_planes_by_countries(self, countries: List[str]) -> List[Tuple[str, str, float, float]]:
        """Получает список самолетов по переданным названиям стран.

        Args:
            countries: Список названий стран (например, ['USA', 'Russia'])

        Returns:
            List[Tuple[str, str, float, float]]: (позывной, страна, скорость, высота)
        """
        if not countries:
            return []

        # Формируем LIKE условия для поиска по частичному совпадению
        like_conditions = ' OR '.join([f"registration_country ILIKE '%%{c}%%'" for c in countries])

        with self._get_connection() as conn:
            with conn.cursor() as cur:
                query = f"""
                    SELECT callsign, registration_country, velocity, altitude
                    FROM aeroplanes
                    WHERE on_ground = false AND ({like_conditions})
                    ORDER BY altitude DESC
                """
                cur.execute(query)
                return cur.fetchall()
