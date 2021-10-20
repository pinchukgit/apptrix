FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN pip install django
RUN pip install gunicorn
RUN pip install django-filter
RUN pip install djangorestframework
RUN pip install beautifulsoup4
RUN pip install psycopg2
RUN pip install Pillow
RUN pip install djangorestframework-jwt
RUN pip install requests
RUN pip install celery
RUN pip install redis