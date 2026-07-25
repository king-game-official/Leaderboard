# Leaderboard API

Простой сервер для сохранения рекордов игроков в таблицу лидеров. Написан на Flask, использует MongoDB.

## API

- `POST /score` — сохранить или обновить рекорд.  
  Требует заголовок `X-API-Key` и JSON: `{"player": "Имя", "score": 123}`.
- `GET /leaderboard` — получить топ-10 игроков.  
  Ответ: `[{"player": "...", "score": ...}, ...]`

## Переменные окружения

- `API_SECRET_KEY` — секретный ключ для защиты.
- `MONGO_URI` — строка подключения к MongoDB Atlas.

## Локальный запуск

```bash
pip install -r requirements.txt
export API_SECRET_KEY="ваш_ключ"
export MONGO_URI="mongodb+srv://..."
python app.py
```

## Деплой на Render

1. Загрузите код на GitHub.
2. На Render создайте Web Service, укажите репозиторий.
3. В настройках добавьте переменные окружения.
4. Команда сборки: `pip install -r requirements.txt`  
   Команда запуска: `gunicorn app:app`
