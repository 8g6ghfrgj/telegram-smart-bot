FROM python:3.11-slim

# منع كتابة pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نسخ المتطلبات أولاً (تحسين build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ المشروع كامل
COPY . .

# تشغيل البوت
CMD ["python", "bot/main.py"]
