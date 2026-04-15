# ── Frontend: Streamlit App ──
FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and config
COPY main.py .
COPY .streamlit/ .streamlit/

EXPOSE 8501

# Streamlit config: disable CORS/XSRF for Docker, set server address
CMD ["streamlit", "run", "main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
