FROM python:3.8.20

WORKDIR /app

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set environment variables for the application
ENV ENVIRONMENT=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Ensure the uploads directory exists
RUN mkdir -p app/static/uploads/pets app/static/uploads/lost_pet_reports


# Run the application
CMD /bin/bash -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"