# Cashback Categories App

Небольшое FastAPI-приложение для хранения категорий кэшбека по пользователям и картам в JSON-файле.
Поддерживает добавление пользователей, карт и новых категорий кэшбека через интерфейс.
Интеграция с Ollama вынесена в отдельный worker, а взаимодействие между сервисами идёт через NATS.

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
По умолчанию worker ожидает локальную Ollama на хосте по адресу `http://host.docker.internal:11434`.
Если у вас есть отдельный сервер с Ollama, можно указать его адрес в `.env`.

Пример `.env.example` уже добавлен в проект, а `.env` исключён из git.

Пример `.env` для внешнего сервера:

```env
OLLAMA_BASE_URL=http://192.168.1.50:11434
```

После первого запуска нужно загрузить хотя бы одну модель, например:

```bash
ollama pull llama3.1:8b
```

После этого на странице `http://127.0.0.1:8000/summary` можно выбрать пользователя, модель и задать вопрос:

```text
По какой карте лучше купить продукты?
По какой карте лучше оплатить такси?
Какая карта лучше подойдет для покупки билетов на самолет?
```

## Тесты

Базовые тесты лежат в `tests/`, а фикстуры JSON вынесены в `tests/fixtures/`.

Запуск в Docker:

```bash
make docker-build
make docker-test
```

Если нужно поднять приложение на тестовых JSON-фикстурах вручную:

```bash
make run-test-data
```

Эта команда копирует фикстуры в `.tmp/test_data` и запускает приложение с `TEST_DATA_DIR=.tmp/test_data`.
Основной UI будет работать на тестовых данных. NATS и Ollama понадобятся только если использовать чат на странице summary.

## Структура проекта

```text
app/
  api/routes/        # HTTP-маршруты основного приложения
  core/              # конфигурация
  schemas/           # pydantic-схемы
  services/          # работа с JSON и gateway к NATS
  main.py            # точка входа основного FastAPI

ollama_service/
  core/              # конфигурация сервиса
  schemas/           # схемы запросов
  services/          # работа с Ollama и prompt builder
  worker.py          # отдельный NATS worker для LLM

shared/
  nats_subjects.py   # общие subjects для обмена через NATS
```

В `docker compose` поднимаются три сервиса:

1. `cashback-app` — основной web backend и frontend.
2. `ollama-worker` — отдельный worker, который получает задачи через NATS.
3. `nats` — брокер сообщений.

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
