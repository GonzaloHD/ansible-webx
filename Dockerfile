FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential \
    libmagic1 \
    openssh-client \
    vim \
    curl \
    && apt-get clean

# Copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# Switch working directory
WORKDIR /app

# Install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# Copy every content from the local file to the image
COPY . /app

# Set the entrypoint to execute the python module
ENTRYPOINT [ "python3", "-m", "ansible_webx.app.run" ]

# Expose port for the server
EXPOSE 5005
