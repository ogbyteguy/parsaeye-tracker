FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد
COPY . .

# ایجاد پوشه data
RUN mkdir -p data

# متغیر محیطی
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# اجرا
CMD ["python", "-m", "bot.main"]
