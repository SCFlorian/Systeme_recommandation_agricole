FROM python:3.12-slim

WORKDIR /app

# Installation des outils nécessaires
RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copie des fichiers de dépendances
COPY pyproject.toml poetry.lock* ./

# Installation des librairies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Copie du reste du code (les datasets et modèles sont ignorés via .gitignore)
COPY . .

# Port exposé par Hugging Face
EXPOSE 7860

# Script de lancement
CMD uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run streamlit.py --server.port 7860 --server.address 0.0.0.0