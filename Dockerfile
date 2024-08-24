# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Expose port 8000 for FastAPI and 8501 for Streamlit
EXPOSE 8080 8000

# Run the start script
#CMD ["sh", "/app/start.sh"]

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit/Home.py --server.port 8080 --server.enableCORS false"]
