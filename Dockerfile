FROM python:3.9-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Abhängigkeiten für Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcb-dri3-0 wget \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren
RUN pip install poetry \
    && poetry config virtualenvs.create false

# Projekt-Metadaten kopieren und Abhängigkeiten installieren
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --without dev --no-interaction

# Restlichen Code kopieren
COPY . /app

# Playwright-Browser installieren
RUN playwright install --with-deps

# Port freigeben
EXPOSE 8000

# Start-Kommando
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
