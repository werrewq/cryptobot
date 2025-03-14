# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.10-bookworm
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /app
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY /bot/requirements.txt /app
RUN pip3 install --upgrade pip -r requirements.txt
# |ВАЖНЫЙ МОМЕНТ| копируем содержимое папки, где находится Dockerfile,
# в рабочую директорию контейнера
COPY /bot /app/bot
# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 8000
# Устанавливаем PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"