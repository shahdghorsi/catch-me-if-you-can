FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p instance
ENV PORT=8080
EXPOSE 8080
CMD exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
