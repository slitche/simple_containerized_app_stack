FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# main application code
COPY app/ app/

# will be used for testing DB connection
# COPY generate_sample_users.py .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# app.main because main.py is inside the "app" folder