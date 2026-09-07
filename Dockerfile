FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Collect static files (if Django settings configured)
RUN python manage.py collectstatic --noinput || true

# Default port for many platforms (Vercel provides $PORT)
ENV PORT 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "3"]
