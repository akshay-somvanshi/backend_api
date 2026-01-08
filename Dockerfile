FROM python:3.12-slim

WORKDIR /app

# Copy requirements 
COPY requirements.txt .

# Install required libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy current directory 
COPY . . 

# Container listens to port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "debug"]