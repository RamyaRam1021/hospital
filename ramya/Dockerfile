# Use a lightweight Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that the application will run on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]
