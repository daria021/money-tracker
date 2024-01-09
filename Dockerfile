FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /bot

RUN pip install --upgrade pip

COPY requirements.txt /bot/

RUN pip install -r requirements.txt

COPY . /bot