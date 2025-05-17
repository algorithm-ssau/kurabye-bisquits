# 🍪 [Kurabye Bisquits - Онлайн магазин кондитерских изделий](http://dev-vexyzy.ru)

Хостинг: https://dev-vexyzy.ru

Добро пожаловать в "Kurabye Bisquits" – восхитительный мир свежей выпечки и сладостей! Это FastAPI приложение представляет собой бэкенд для онлайн-магазина кондитерских изделий, с каталогом продукции, управлением корзиной, оформлением заказов и аутентификацией пользователей.

## Структура проекта
```
kurabye-bisquits-main/
├── app/
│   ├── api/                  # API эндпоинты
│   │   └── v1/               # v1 версия эндпоитнов
│   │       └── endpoints/    # Роутеры для auth, cart, product, admin
│   ├── core/                 # Основная конфигурация, настройки БД, логирование
│   ├── domain/               # Бизнес-логика: сущности, перечисления, исключения
│   ├── models/               # SQLAlchemy модели
│   ├── repository/           # Слой доступа к данным (реальные и fake репозитории)
│   │   └── sql/              # SQL запросы
│   ├── schemas/              # Pydantic схемы для валидации данных API
│   ├── services/             # Сервисный слой (бизнес-логика)
│   ├── static/               # Статические файлы (CSS, JS, изображения)
│   ├── templates/            # HTML шаблоны (Jinja2)
│   ├── utils/                # Вспомогательные утилиты (аутентификация, работа с корзиной)
│   └── app.py                # Главный файл приложения FastAPI
├── logs/                     # Директория для лог-файлов
├── tests/                    # Юнит и интеграционные тесты
├── .env.example              # Пример файла переменных окружения (создайте свой .env)
├── pyproject.toml            # Описание проекта и его зависимостей для PEP 517/PEP 621
├── uv.lock                   # Lock-файл для зависимостей (генерируется uv)
└── README.md                 # Этот файл
```

## 🛠️ Технологический стек

*   **Бэкенд:**
    *   Python 3.13+
    *   FastAPI
    *   SQLAlchemy (асинхронный режим с AsyncPG)
    *   PostgreSQL
    *   Uvicorn (ASGI сервер)
    *   Pydantic (валидация данных)
    *   Passlib[bcrypt] (хеширование паролей)
    *   PyJWT (работа с JSON Web Tokens)
    *   Sentry-SDK (мониторинг ошибок)
    *   UV (менеджер пакетов и установщик)
*   **Фронтенд (примеры):**
    *   HTML5, CSS3
    *   JavaScript (Vanilla JS для взаимодействия с API)
    *   Jinja2 (шаблонизация)
*   **База Данных:**
    *   PostgreSQL
*   **Инструменты:**
    *   Docker, Docker Compose
    *   Nginx / Apache (для reverse proxy в production)
    *   Ruff (линтер и форматер)
    *   Pyright (проверка типов)

## 🚀 Начало работы

### Предварительные требования

*   Python 3.13+
*   PostgreSQL (если не используется Docker для БД)
*   `uv` ([официальная документация](https://docs.astral.sh/uv/))

### 1. Клонирование репозитория

```bash
git clone https://github.com/algorithm-ssau/kurabye-bisquits
cd kurabye-bisquits
```

### 2. Настройка окружения

Создайте файл .env в корневой директории проекта (kurabye-bisquits) на основе примера .env_example.

### 3. Перейдите в /app и запустите приложение

```bash
cd app/
uv run app.py &
```

Приложение будет доступно по адресу http://localhost:8000.

Веб-интерфейс: http://localhost:8000
Документация API (ReDoc): http://localhost:8000/redoc

## 📜 API Эндпоинты

Основные эндпоинты находятся по префиксу /api/v1/.

Аутентификация (/api/v1/auth):

POST /token: Получение JWT токена (логин).

POST /registration: Регистрация нового пользователя.

GET /protected: Пример защищенного эндпоинта.

Каталог (/api/v1/product):

GET /all: Получение списка продуктов с пагинацией и сортировкой.

GET /: Получение детальной информации о продукте по ID.

Корзина (/api/v1/cart):

GET /: Получение содержимого корзины пользователя.

PATCH /{product_id}: Добавление/обновление количества товара в корзине.

DELETE /{product_id}: Удаление товара из корзины.

POST /create_order: Создание заказа из корзины.

GET /get_user_orders: Получение списка заказов пользователя.

GET /get_order: Получение деталей конкретного заказа.

Детальное описание эндпоинтов доступно в Swagger документации по адресу /redoc после запуска приложения.

## 🤝 Команда разработчиков

| Аватар | Имя | Должность |
|:------:|:---|:---------|
| <img src="https://github.com/algorithm-ssau/kurabye-bisquits/blob/main/app/static/img/van.jpg"  alt="Avatar" style="border-radius: 20px; width: 200px; height: 200px;"> | Никулин Иван | TeamLead |
| <img src="https://github.com/algorithm-ssau/kurabye-bisquits/blob/main/app/static/img/alena.jpg" alt="Avatar" style="border-radius: 20px; width: 200px; height: 200px;"> | Алёна Соколова | Дизайнер интерфейсов, frontend разработчик |
| <img src="https://github.com/algorithm-ssau/kurabye-bisquits/blob/main/app/static/img/denis1.jpg" alt="Avatar" style="border-radius: 20px; width: 200px; height: 200px;"> | Денис Мотяков | Backend разработчик, разработчик баз данных |
| <img src="https://github.com/algorithm-ssau/kurabye-bisquits/blob/main/app/static/img/andrey.png" style="border-radius: 20px; width: 200px; height: 200px;"> | Телегин Андрей |  Fullstack разработчик |
