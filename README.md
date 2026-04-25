# Мониторинг самолетов / Airplanetracker_advanced

Учебный проект. Программа собирает данные о самолетах в воздушном пространстве различных стран через API OpenSky Network и сохраняет их в PostgreSQL.

## Возможности

- Сбор данных о самолетах для 10+ стран
- Сохранение информации в базу данных (PostgreSQL)
- Анализ данных: средняя высота, топ самолетов, фильтрация по странам
- Консольный интерфейс для работы с данными

## Требования

- Python 3.12+
- PostgreSQL
- Poetry

### Установка
```bash
# Клонировать репозиторий
git clone <https://github.com/kev7570-debug/Airplanetracker_advanced>
cd pythonProject1

# Установить зависимости
poetry install
```

### Настройка базы данных
1. Создайте файл database.ini в корне проекта:

[postgresql]
host=localhost
user=postgres
password=ваш_пароль
port=5432

2. Убедитесь, что PostgreSQL запущен

Запуск
poetry run python main.py

#### Структура проекта

├── src/
│   ├── api_module.py       # Работа с API (OpenSky, Nominatim)
│   ├── aeroplane_module.py # Класс самолета
│   ├── db_manager.py       # Работа с базой данных
│   └── db_utils.py         # Создание БД и таблиц
├── main.py                 # Точка входа
├── config.py               # Чтение конфигурации
├── pyproject.toml          # Зависимости
└── database.ini            # Настройки БД

##### База данных
countries — таблица со странами и их координатами
aeroplanes — таблица с самолетами 

##### Используемые API
OpenSky Network (данные о самолетах) - публичный API без авторизации
Nominatim OpenStreetMap (координаты стран) - бесплатный сервис с открытым доступом, не требует ключа

###### Автор

Автор проекта: Елена Кашина 
Контакт: kev7570@gmail.com
2026
---

Если у вас есть вопросы или пожелания по улучшению проекта, обращайтесь.