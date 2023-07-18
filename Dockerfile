FROM python:3.10.11-bullseye

ENV POETRY_VERSION 1.5.1
ENV GECKODRIVER_VERSION 0.33.0

# Set python-specific environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ./app

# Install Firefox and geckodriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates curl firefox-esr && \
    curl -L https://github.com/mozilla/geckodriver/releases/download/v$GECKODRIVER_VERSION/geckodriver-v$GECKODRIVER_VERSION-linux64.tar.gz | tar xz -C /usr/local/bin && \
    apt-get purge -y ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -y && apt-get upgrade -y

# Install poetry and app dependencies
RUN pip install poetry==$POETRY_VERSION && \
    poetry config virtualenvs.create false

COPY ./app/pyproject.toml ./app/poetry.lock .
RUN poetry install

COPY ./app .

CMD python3 main.py


