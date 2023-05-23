# Dockerfile
FROM python:3.10.4

RUN apt-get update && apt-get install -y tzdata

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /app/logs
COPY ./common /app/common
COPY . ./log_monitoring

ENV PYTHONPATH "${PYTHONPATH}:/log_monitoring/common"

EXPOSE 5006

CMD ["python", "./log_monitoring/service.py"]
