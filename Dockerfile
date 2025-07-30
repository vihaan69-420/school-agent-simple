FROM python:3.10-slim

WORKDIR /app

COPY backend/ ./backend/

WORKDIR /app/backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "main_production.py"]
