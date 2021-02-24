FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install Pillow \
  django-cleanup \
  requests
COPY . /code/