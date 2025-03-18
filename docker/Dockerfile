FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

ARG GID=1000
ARG UID=1000
ARG USER=ubuntu

RUN apt-get update && apt-get upgrade -y \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y

RUN addgroup -gid $GID --system $USER \
  && adduser --system $USER --gid $GID --disabled-password --uid "$UID"

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

USER $USER
