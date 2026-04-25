"""Модуль для взаимодействия с API OpenSky Network и Nominatim."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class BaseAPI(ABC):
    """Абстрактный класс для работы с API."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> List[Dict[str, Any]]:
        """Получение информации о самолетах по названию страны."""
        pass


class AeroplanesAPI(BaseAPI):
    """Класс для работы с API самолетов."""

    def __init__(self) -> None:
        """Инициализация с приватными атрибутами."""
        self.__openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.__opensky_url = 'https://opensky-network.org/api/states/all'

    def _connect(self, url: str, params: Dict[str, Any] = None) -> Any:
        """Приватный метод подключения к API с проверкой статус-кода."""
        try:
            headers = {}
            if 'nominatim' in url:
                headers = {'User-Agent': 'skypro-coursework/1.0'}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # проверка статус-кода
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка подключения к API: {e}")

    def __get_country_coordinates(self, country: str) -> Dict[str, float]:
        """Приватный метод получения координат страны."""
        params = {
            'country': country,
            'format': 'json',
            'limit': 1
        }

        data = self._connect(self.__openstreetmap_url, params)

        if not data:
            raise ValueError(f"Страна '{country}' не найдена")

        bounding_box = data[0].get('boundingbox')
        return {
            'lamin': float(bounding_box[0]),
            'lamax': float(bounding_box[1]),
            'lomin': float(bounding_box[2]),
            'lomax': float(bounding_box[3])
        }

    def get_aeroplanes(self, country: str) -> List[Dict[str, Any]]:
        """Получение данных о самолетах в воздушном пространстве страны."""
        coordinates = self.__get_country_coordinates(country)
        data = self._connect(self.__opensky_url, coordinates)
        return data.get('states', [])
