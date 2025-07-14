ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION} AS python

FROM python AS builder

ARG BUILD_ENVIRONMENT=prod

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/src/app/wheels

COPY ./requirements/base.txt ./requirements/base.txt
COPY ./requirements/${BUILD_ENVIRONMENT}.txt ./requirements/${BUILD_ENVIRONMENT}.txt

RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r "./requirements/${BUILD_ENVIRONMENT}.txt"

FROM python AS runner

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ="Europe/Istanbul"

RUN apt-get update && apt-get install --no-install-recommends -y \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/wheels /wheels/
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY . .