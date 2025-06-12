ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS python

# Python build stage
FROM python AS python-build-stage

# Install build dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached
ARG BUILD_ENVIRONMENT=local
COPY ./requirements /requirements

# Create Python wheels
RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r "/requirements/${BUILD_ENVIRONMENT}.txt"

# Python runtime stage
FROM python AS python-run-stage

ARG APP_HOME=/code
WORKDIR ${APP_HOME}

# Install runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq5 \
    curl \
    nodejs \
    npm \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy Python wheels from build stage and install
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# Create app user for security
RUN groupadd -r django && useradd -r -g django django

# Copy application code
COPY --chown=django:django . ${APP_HOME}

# Install Node.js dependencies and build CSS
COPY package*.json ./
RUN npm ci --only=production && npm run build-css-prod

# Create logs directory
RUN mkdir -p ${APP_HOME}/logs && chown django:django ${APP_HOME}/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=${APP_HOME}
ENV TZ="Europe/Istanbul"

# Switch to non-root user
USER django

# Run Django collectstatic
RUN python manage.py collectstatic --noinput --settings=skillforge.settings.base || true

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]