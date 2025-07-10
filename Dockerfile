# build api at deployment
FROM python:3.12-slim

# Copy application code
COPY ./ .

# Install dependencies
RUN pip install --no-cache-dir -r 'requirements.txt'

# Set workdir
WORKDIR /src

# Default command (overwritten by docker-compose)
CMD ["uvicorn", "backend.api:api", "--host", "0.0.0.0", "--port", "8080"]
