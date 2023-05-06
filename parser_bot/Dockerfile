# Dockerfile
FROM python:3.10.4

WORKDIR /parser_bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "bot.py"]
