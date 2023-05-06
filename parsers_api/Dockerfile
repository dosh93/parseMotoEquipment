# Dockerfile
FROM python:3.10.4

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./common /app/common
COPY . ./parsers_api

ENV PYTHONPATH "${PYTHONPATH}:/app/common"

EXPOSE 5002

CMD ["python", "./parsers_api/server.py"]
