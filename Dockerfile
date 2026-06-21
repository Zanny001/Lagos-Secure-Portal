# Use an official, lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the cloud container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Zannie architecture into the container
COPY . .

# Expose the specific port the app runs on
EXPOSE 5001

# Define environment variables for production security
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Run the master node when the container launches
CMD ["python3", "app.py"]
