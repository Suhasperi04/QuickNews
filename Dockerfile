FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for slides and links
RUN mkdir -p slides links

# Run the scheduler
CMD ["python", "scheduler.py"]
