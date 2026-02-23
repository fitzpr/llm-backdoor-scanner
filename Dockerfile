
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy scanner files
COPY scan_model.py .
COPY attention_monitor.py .
COPY visualization.py .

# Create baselines directory
RUN mkdir -p /app/baselines

# Expose API port
EXPOSE 8000

# Default command
CMD ["python", "scan_model.py", "--help"]
