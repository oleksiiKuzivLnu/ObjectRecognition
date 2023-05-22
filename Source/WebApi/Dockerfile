# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000:80

# Run app.py when the container launches
CMD ["python", "app.py"]
