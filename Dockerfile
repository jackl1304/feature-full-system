FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libx11-xcb1 libxcb-dri3-0 wget \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry \
  && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --without dev --no-interaction

COPY . /app

RUN playwright install --with-deps

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
