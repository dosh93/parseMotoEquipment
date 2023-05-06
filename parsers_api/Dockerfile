# Dockerfile
FROM python:3.10.4

WORKDIR /parsers_api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "server.py"]
