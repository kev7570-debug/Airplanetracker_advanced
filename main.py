"""Главный модуль - точка входа в программу."""

import os
import sys

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import config
from src.aeroplane_module import Aeroplane
from src.api_module import AeroplanesAPI
from src.db_manager import DBManager
from src.db_utils import create_database, create_tables

# Список стран для мониторинга (10+ стран)
COUNTRIES = [
    "United States",
    "Canada",
    "United Kingdom",
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Russia",
    "Japan",
    "Australia",
    "Brazil",
    "India"
]


def print_planes_table(planes: list, title: str = "Самолеты"):
    """Вывод списка самолетов в виде таблицы.

    Поддерживает два формата данных:
    1. (callsign, country, velocity, altitude) - 4 элемента
    2. (callsign, altitude, country) - 3 элемента (для get_max_height)
    """
    if not planes:
        print(f"\n{title}: не найдено")
        return

    print(f"\n{'=' * 80}")
    print(f"{title}: найдено {len(planes)} самолетов")
    print('=' * 80)
    print(f"{'Позывной':<15} {'Страна':<20} {'Скорость':<12} {'Высота':<12}")
    print('-' * 80)

    for plane in planes:
        # Определяем формат данных по длине кортежа
        if len(plane) == 4:
            # Формат: (callsign, country, velocity, altitude)
            callsign, country, velocity, altitude = plane
        elif len(plane) == 3:
            # Формат: (callsign, altitude, country) - для get_max_height
            callsign, altitude, country = plane
            velocity = 0.0  # Скорость неизвестна в этом запросе
        else:
            continue

        # Расчет скорости в км/ч (если есть данные)
        if velocity and isinstance(velocity, (int, float)):
            speed_kmh = velocity * 3.6
            speed_str = f"{velocity:.1f} м/с ({speed_kmh:.1f} км/ч)"
        else:
            speed_str = "нет данных"

        print(f"{callsign:<15} {country:<20} {speed_str:<25} {altitude:>8.1f} м")


def print_countries_table(countries_data: list):
    """Вывод списка стран с количеством самолетов."""
    if not countries_data:
        print("Нет данных о странах")
        return

    print(f"\n{'=' * 60}")
    print("Страны и количество самолетов в воздушном пространстве")
    print('=' * 60)
    print(f"{'Страна':<30} {'Количество самолетов':<20}")
    print('-' * 60)

    for country, count in countries_data:
        print(f"{country:<30} {count:<20}")


def collect_data_for_countries(api: AeroplanesAPI, db_manager: DBManager) -> None:
    """Сбор данных о самолетах для всех стран из списка.

    Args:
        api: Экземпляр API для запросов
        db_manager: Экземпляр DBManager для сохранения
    """
    print("\n" + "=" * 60)
    print("Сбор данных о самолетах по странам")
    print("=" * 60)

    for country in COUNTRIES:
        print(f"\nОбработка: {country}...")

        try:
            # Получаем данные через API
            aeroplanes_data = api.get_aeroplanes(country)

            if not aeroplanes_data:
                print("  - Самолеты не найдены")
                continue

            # Преобразуем в объекты
            aeroplanes = Aeroplane.cast_to_object_list(aeroplanes_data)
            print(f"  - Найдено самолетов: {len(aeroplanes)}")

            # Получаем координаты страны
            coordinates = api._AeroplanesAPI__get_country_coordinates(country)

            # Сохраняем страну в БД
            country_id = db_manager.save_country_data(country, coordinates)

            # Сохраняем самолеты в БД
            db_manager.save_aeroplanes(country_id, aeroplanes)
            print("  - Данные сохранены в БД")

        except Exception as e:
            print(f"  - Ошибка: {e}")


def user_interaction(db_manager: DBManager) -> None:
    """Главная функция взаимодействия с пользователем."""
    print("\n" + "=" * 60)
    print("Программа для мониторинга самолетов")
    print("=" * 60)

    while True:
        print("\nВыберите действие:")
        print("1. Список стран и количество самолетов")
        print("2. Список всех самолетов (позывной, страна, скорость, высота)")
        print("3. Средняя высота полета всех самолетов")
        print("4. Самолеты, летящие выше средней высоты")
        print("5. Поиск самолетов по странам (например, USA, Russia)")
        print("0. Выход")

        choice = input("\nВаш выбор: ").strip()

        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            data = db_manager.get_info_countries_and_planes()
            print_countries_table(data)

        elif choice == '2':
            data = db_manager.get_all_planes()
            print_planes_table(data, "Все самолеты в воздухе")

        elif choice == '3':
            avg_height = db_manager.get_avg_height()
            print(f"\nСредняя высота полета всех самолетов: {avg_height:.2f} м")

        elif choice == '4':
            data = db_manager.get_max_height()
            print_planes_table(data, "Самолеты, летящие выше средней высоты")

        elif choice == '5':
            countries_input = input("Введите названия стран через запятую (например, USA, Russia): ")
            countries = [c.strip() for c in countries_input.split(',') if c.strip()]
            if countries:
                data = db_manager.get_planes_by_countries(countries)
                print_planes_table(data, f"Самолеты из стран: {', '.join(countries)}")
            else:
                print("Страны не указаны")

        else:
            print("Неверный выбор. Попробуйте снова.")


def main():
    """Основная функция программы."""
    # Параметры подключения к БД
    db_params = config()
    db_name = "aeroplanes_db"

    try:
        # Создаем базу данных
        create_database(db_name, db_params)

        # Создаем таблицы
        create_tables(db_name, db_params)

        # Инициализируем API и DBManager
        api = AeroplanesAPI()
        db_manager = DBManager(db_name, db_params)

        # Собираем данные по всем странам
        collect_data_for_countries(api, db_manager)

        # Запускаем интерфейс пользователя
        user_interaction(db_manager)

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
