FROM python:3.10.6-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV TINI_VERSION=v0.19.0

ARG TARGETARCH

# System deps:
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    curl \
    gcc \
    libc-dev \
    git \
  # Installing `tini` utility:
  # https://github.com/krallin/tini
  && if [ "$TARGETARCH" = "arm64" ]; then TINI_EXE=tini-arm64; else TINI_EXE=tini; fi \
  && curl -Lo /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/${TINI_EXE}" \
  && chmod +x /usr/local/bin/tini && tini --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y


WORKDIR /app

COPY requirements.txt .
COPY requirements.dev.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt -r requirements.dev.txt

COPY . .

ENTRYPOINT ["tini", "--"]
