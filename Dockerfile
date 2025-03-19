# Выкачиваем из dockerhub образ с python версии 3.9
FROM python:3.10-slim
# копируем файлы проекта
COPY . .
# обновляем окружени
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Команда EXPOSE не открывает порт или не перенаправляет его на хост-машину, а просто сообщает Docker, что контейнер будет слушать на указанном порту во время выполнения
# EXPOSE 80
# CMD gunicorn bot.main:"main()" -b 0.0.0.0:8000 --reload
CMD ["gunicorn", "bot.main:start_bot()", "-b", "0.0.0.0:80", "--reload"]