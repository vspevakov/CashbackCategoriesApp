# Cashback Categories App

Небольшое FastAPI-приложение для хранения категорий кэшбека по пользователям и картам в JSON-файле.
Поддерживает добавление пользователей, карт и новых категорий кэшбека через интерфейс.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска откройте `http://127.0.0.1:8000`.

## Запуск через Docker

```bash
docker compose up --build
```

После запуска приложение будет доступно на `http://127.0.0.1:8000`.

JSON-файлы с данными сохраняются в локальной директории `data/`, она примонтирована в контейнер как volume.

## Структура данных

Данные сохраняются в `data/cashback_data.json` в формате:

```json
{
  "Иван": {
    "Tinkoff Black": {
      "Супермаркеты": {
        "enabled": true,
        "percent": 5
      },
      "Рестораны и кафе": {
        "enabled": false,
        "percent": 0
      }
    }
  }
}
```
