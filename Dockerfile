FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=Ofertum.settings
ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "Ofertum.wsgi:application", "--bind", "0.0.0.0:8000"]
