"""Модуль для работы с информацией о самолетах."""

from typing import Any, Dict, List

# from datetime import datetime


class Aeroplane:
    """Класс для представления информации о самолете."""

    __slots__ = ('__icao24', '__callsign', '__country', '__velocity',
                 '__altitude', '__latitude', '__longitude', '__on_ground')

    def __init__(self, icao24: str, callsign: str, country: str,
                 velocity: float, altitude: float,
                 latitude: float, longitude: float,
                 on_ground: bool = False) -> None:
        """Инициализация с валидацией данных."""
        self.__icao24 = self.__validate_string(icao24, "ICAO24")
        self.__callsign = self.__validate_string(callsign, "Позывной")
        self.__country = self.__validate_string(country, "Страна")
        self.__velocity = self.__validate_positive_float(velocity, "Скорость")
        self.__altitude = self.__validate_positive_float(altitude, "Высота")
        self.__latitude = self.__validate_coordinate(latitude, "Широта", -90, 90)
        self.__longitude = self.__validate_coordinate(longitude, "Долгота", -180, 180)
        self.__on_ground = bool(on_ground)

    # Геттеры
    @property
    def icao24(self) -> str:
        return self.__icao24

    @property
    def callsign(self) -> str:
        return self.__callsign

    @property
    def country(self) -> str:
        return self.__country

    @property
    def velocity(self) -> float:
        return self.__velocity

    @property
    def altitude(self) -> float:
        return self.__altitude

    @property
    def latitude(self) -> float:
        return self.__latitude

    @property
    def longitude(self) -> float:
        return self.__longitude

    @property
    def on_ground(self) -> bool:
        return self.__on_ground

    # Приватные методы валидации
    @staticmethod
    def __validate_string(value: str, field_name: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError(f"{field_name} должен быть непустой строкой")
        return value.strip()

    @staticmethod
    def __validate_positive_float(value: float, field_name: str) -> float:
        try:
            value = float(value)
            if value < 0:
                raise ValueError
            return value
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} должен быть неотрицательным числом")

    @staticmethod
    def __validate_coordinate(value: float, field_name: str,
                              min_val: float, max_val: float) -> float:
        try:
            value = float(value)
            if not min_val <= value <= max_val:
                raise ValueError
            return value
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} должна быть в диапазоне [{min_val}, {max_val}]")

    # Магические методы для сравнения по высоте и скорости
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return False
        return self.__velocity == other.__velocity and self.__altitude == other.__altitude

    def __lt__(self, other: 'Aeroplane') -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self.__velocity, self.__altitude) < (other.__velocity, other.__altitude)

    def __gt__(self, other: 'Aeroplane') -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return (self.__velocity, self.__altitude) > (other.__velocity, other.__altitude)

    # Фабричные методы
    @classmethod
    def from_api_data(cls, api_data: List[Any]) -> 'Aeroplane':
        """Создание объекта из данных API."""
        if not api_data or len(api_data) < 10:
            raise ValueError("Недостаточно данных для создания объекта")

        return cls(
            icao24=api_data[0],
            callsign=api_data[1].strip() if api_data[1] else "Unknown",
            country=api_data[2],
            velocity=float(api_data[9]) if api_data[9] is not None else 0.0,
            altitude=float(api_data[7]) if api_data[7] is not None else 0.0,
            latitude=float(api_data[6]),
            longitude=float(api_data[5]),
            on_ground=bool(api_data[8])
        )

    @staticmethod
    def cast_to_object_list(aeroplanes_data: List[List[Any]]) -> List['Aeroplane']:
        """Преобразование списка данных в список объектов."""
        result = []
        for data in aeroplanes_data:
            try:
                result.append(Aeroplane.from_api_data(data))
            except (ValueError, IndexError) as e:
                print(f"Ошибка создания объекта: {e}")
                continue
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для сохранения."""
        return {
            'icao24': self.__icao24,
            'callsign': self.__callsign,
            'country': self.__country,
            'velocity': self.__velocity,
            'altitude': self.__altitude,
            'latitude': self.__latitude,
            'longitude': self.__longitude,
            'on_ground': self.__on_ground
        }

    def __repr__(self) -> str:
        return f"Aeroplane(callsign='{self.__callsign}', altitude={self.__altitude:.2f} м)"
