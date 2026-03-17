# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your script and install the library
RUN pip install drain3
COPY app.py .

# Run the script when the container starts
CMD ["python", "app.py"]

# -v mounts your host's syslog into the container's syslog
docker run -v /var/log/syslog:/var/log/syslog:ro log-ai-v1