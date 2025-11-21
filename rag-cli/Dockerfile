FROM python:3.12

# Program Prerequisites
COPY requirements.txt .
RUN pip install -r requirements.txt

# Utilities
RUN apt-get update && apt-get install nano sudo -y

# Startup and Entry script
COPY . .
RUN chmod +x app.py
CMD ["python", "app.py"]