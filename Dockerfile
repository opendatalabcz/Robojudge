FROM python:3.10-slim as builder

RUN pip install poetry 

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR

FROM python:3.10-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Installs headless browser and deps for case scraping
RUN playwright install & playwright install-deps

COPY robojudge ./robojudge

EXPOSE 4000

ENTRYPOINT ["python", "-m", "robojudge.main"]