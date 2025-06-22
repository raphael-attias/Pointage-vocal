# Utilise une image Python légère
FROM python:3.11-slim

# Définir le dossier de travail dans le conteneur
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose le port de Streamlit
EXPOSE 8501

# Commande de démarrage
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
