# Dockerfile
FROM python:3.10.4

# Устанавливаем необходимые зависимости для запуска Chromium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/logs
COPY ./common /app/common
COPY . ./parsers_api

ENV PYTHONPATH "${PYTHONPATH}:/app/common"

EXPOSE 5002

CMD ["python", "./parsers_api/server.py"]
