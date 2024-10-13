# Use the official Ubuntu base image
FROM ubuntu:22.04

# Set environment variables to avoid user input prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11, pip, and other necessary packages
RUN apt-get update && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    build-essential \
    libpq-dev \
    && apt-get clean

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Set up a working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the Django application code into the container
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Set environment variables to ensure Python outputs are not buffered
ENV PYTHONUNBUFFERED=1

# Run the Django development server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]