# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.10-bookworm
# Устанавливаем рабочую директорию для проекта в контейнере
WORKDIR /app
# Скачиваем/обновляем необходимые библиотеки для проекта
COPY requirements.txt /app
RUN pip3 install --upgrade pip -r requirements.txt
# |ВАЖНЫЙ МОМЕНТ| копируем содержимое папки, где находится Dockerfile,
# в рабочую директорию контейнера
COPY . /app/bot
# Устанавливаем порт, который будет использоваться для сервера
EXPOSE 5001
# Устанавливаем PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"