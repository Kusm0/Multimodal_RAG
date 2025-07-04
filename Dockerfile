FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gradio сам відкриє порт, тому достатньо запустити скрипт
EXPOSE 7860
CMD ["python", "-m", "app.main"]