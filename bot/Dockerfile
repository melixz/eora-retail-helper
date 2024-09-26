# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Обновляем пакетный менеджер и устанавливаем ca-certificates
RUN apt-get update && apt-get install -y ca-certificates

# Копируем сертификаты
COPY ./certs/combined_ca.crt /app/certs/combined_ca.crt

# Команда для запуска приложения
CMD ["python", "/app/main.py"]
