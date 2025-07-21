FROM python:3.9-slim

# 1) Basis-Dependencies installieren (Playwright benötigt native libs)
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libx11-xcb1 libxcb-dri3-0 wget \
  && rm -rf /var/lib/apt/lists/*

# 2) Arbeitsverzeichnis setzen (hier landet das gesamte Repo)
WORKDIR /app

# 3) Poetry installieren
RUN pip install poetry \
  && poetry config virtualenvs.create false

# 4) Projekt-Metadaten kopieren und Abhängigkeiten installieren
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --without dev --no-interaction

# 5) Restlichen Code kopieren
COPY . /app

# 6) Playwright-Browser-Binaries installieren
RUN playwright install --with-deps

# 7) Port freigeben
EXPOSE 8000

# 8) Start-Kommando
#    uvicorn sucht hier /app/src/app.py und erwartet, dass 'src' ein Python-Package ist.
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
