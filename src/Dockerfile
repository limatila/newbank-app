# build api at deployment
FROM python:3.12-slim

# Build essentials (for py wheel)
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Set the working directory
WORKDIR /usr/app

# Copy requirements and install them (only)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Do NOT copy source code (it will be mounted in dev, defined in volumes option)
