# Dockerfile
FROM python:3.10.4

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/logs
COPY ./common /app/common
COPY . ./service_update_price

ENV PYTHONPATH "${PYTHONPATH}:/app/common"

EXPOSE 5003

CMD ["python", "./service_update_price/service_update.py"]
