# Smena Bot

Telegram бот для управления сменами.

## Запуск через Docker

### Предварительные требования

1. Установите [Docker](https://docs.docker.com/get-docker/)
2. Установите [Docker Compose](https://docs.docker.com/compose/install/)

### Настройка

1. Скопируйте файл с примером переменных окружения:
   ```bash
   cp env.example .env
   ```

2. Отредактируйте файл `.env` и укажите ваши настройки:
   ```
   BOT_TOKEN=your_bot_token_here
   GROUP_ID=your_group_id_here
   ```

### Запуск

#### Через Docker Compose (рекомендуется)

```bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build

# Остановка
docker-compose down
```

#### Через Docker напрямую

```bash
# Сборка образа
docker build -t smena-bot .

# Запуск контейнера
docker run -d --name smena-bot --env-file .env smena-bot

# Остановка и удаление контейнера
docker stop smena-bot
docker rm smena-bot
```

### Просмотр логов

```bash
# Через Docker Compose
docker-compose logs -f

# Через Docker
docker logs -f smena-bot
```

### Обновление бота

```bash
# Остановить контейнер
docker-compose down

# Пересобрать и запустить
docker-compose up --build -d
```
