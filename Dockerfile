# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port (helpful for local documentation, though Cloud Run ignores this)
EXPOSE 8080

# Command to run on container start
# Configures Streamlit to bind to 0.0.0.0 and use the PORT environment variable (required by Cloud Run)
# Defaults to 8501 if PORT is not set (e.g., local run)
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
