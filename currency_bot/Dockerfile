# Dockerfile
FROM python:3.10.4

RUN apt-get update && apt-get install -y tzdata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/logs
COPY ./common /app/common
COPY . ./currency_bot

ENV PYTHONPATH "${PYTHONPATH}:/currency_bot/common"

EXPOSE 5001

CMD ["python", "./currency_bot/bot.py"]
