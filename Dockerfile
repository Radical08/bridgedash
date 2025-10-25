FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE $PORT
CMD python manage.py migrate && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application
