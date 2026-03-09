# Link Cutter

Сервис для сокращения ссылок на FastAPI с авторизацией, пользовательскими alias, статистикой переходов и удалением ссылок по времени жизни.

Для удобства тестирования и наглядности с помощью GPT накидал простую веб страницу: http://man-master.ru

## Основные возможности

- Регистрация и авторизация пользователей
- Создание коротких ссылок
- Пользовательский alias для ссылки
- Поиск ссылок по original URL
- Просмотр статистики по short code
- Удаление ссылок авторизованным пользователем
- Назначение времени удаления ссылки
- Замена short code
- Настройка периода удаления неактивных ссылок

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Docker Compose
- Nginx

## Запуск

```bash
docker compose up -d --build
```

Проверка контейнеров:

```bash
docker compose ps
```

Логи:

```bash
docker compose logs --tail=100
```

После запуска локально сервис доступен по адресу:

```text
http://127.0.0.1:8000
```

## Эндпоинты

### Авторизация

- `POST /auth/register` — регистрация пользователя
- `POST /auth/login` — вход в систему

### Ссылки

- `POST /links` — создать короткую ссылку
- `GET /links/{short_code}/stats` — получить статистику по ссылке
- `GET /links/search?original_url=...` — найти ссылки по original URL
- `DELETE /links/{short_code}` — удалить ссылку
- `POST /links/{short_code}/expire` — назначить время удаления
- `PUT /links/{short_code}` — заменить short code
- `POST /links/shorten/set_n/{n}` — установить N дней неактивности для удаления ссылок

## Примеры запросов

### Регистрация

```bash
curl -X POST http://man-master.ru/auth/register   -H "Content-Type: application/json"   -d '{
    "name": "Alex",
    "email": "alex@example.com",
    "password": "strongpassword"
  }'
```

### Авторизация

```bash
curl -X POST http://man-master.ru/auth/login   -H "Content-Type: application/json"   -d '{
    "email": "alex@example.com",
    "password": "strongpassword"
  }'
```

### Создание короткой ссылки

```bash
curl -X POST http://man-master.ru/links   -H "Content-Type: application/json"   -d '{
    "original_url": "https://example.com/very/long/url",
    "alias": "my-link",
    "length": 6
  }'
```

### Статистика по ссылке

```bash
curl http://man-master.ru/links/my-link/stats
```

### Поиск по original URL

```bash
curl "http://man-master.ru/links/search?original_url=https://example.com/very/long/url"
```

## База данных

Проект использует PostgreSQL.

Основные сущности:

- `users` — пользователи
- `links` — короткие ссылки

## Интерфейс

У сервиса есть тестовый веб-интерфейс для проверки основных ручек.

```
http://man-master.ru
```
