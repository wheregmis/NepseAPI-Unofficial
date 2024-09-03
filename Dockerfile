# Use the Python 3.10 slim image as the base
FROM python:3.10-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git curl

# Copy the requirements file
COPY ./requirements.txt .

# Install the required Python packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Install the NepseUnofficialApi directly from GitHub
RUN pip install --upgrade git+https://github.com/basic-bgnr/NepseUnofficialApi.git

# Copy the rest of the code
COPY . .

# Make sure the script is executable
RUN chmod +x /health_check.sh

# Add a health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /health_check.sh

# Run the application
CMD ["python", "server.py"]
