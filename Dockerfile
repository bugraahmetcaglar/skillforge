ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION} AS python
FROM python AS builder

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    default-libmysqlclient-dev

ARG BUILD_ENVIRONMENT=local

COPY ./requirements /requirements
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
    -r "/requirements/${BUILD_ENVIRONMENT}.txt"

FROM python AS runner

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ="Europe/Istanbul"

COPY --from=builder /usr/src/app/wheels  /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# Copy application code
COPY . .