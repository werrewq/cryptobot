# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.10-slim

# Определяем аргументы сборки
ARG BROKER_API_KEY
ARG BROKER_SECRET_KEY
ARG CRYPTOBOT_API_TOKEN
ARG TELEGRAM_BOT_API_TOKEN

# Устанавливаем переменные среды
ENV BROKER_API_KEY=${BROKER_API_KEY}
ENV BROKER_SECRET_KEY=${BROKER_SECRET_KEY}
ENV CRYPTOBOT_API_TOKEN=${CRYPTOBOT_API_TOKEN}
ENV TELEGRAM_BOT_API_TOKEN=${TELEGRAM_BOT_API_TOKEN}

# копируем файлы проекта
COPY . .
# обновляем окружени
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Команда EXPOSE не открывает порт или не перенаправляет его на хост-машину, а просто сообщает Docker, что контейнер будет слушать на указанном порту во время выполнения
EXPOSE 80
# CMD gunicorn bot.main:"main()" -b 0.0.0.0:8000 --reload
CMD ["gunicorn", "bot.main:start_bot()", "-b", "0.0.0.0:80", "--reload"]