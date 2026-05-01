# Use an official Python runtime as a parent image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_app.py

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements_prod.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements_prod.txt

# Install Playwright browsers (Chromium is usually sufficient for scraping)
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Create the data directory for persistent storage
RUN mkdir -p data

# Expose the port the app runs on
EXPOSE 5001

# Command to run the application using Gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "web_app:app"]
