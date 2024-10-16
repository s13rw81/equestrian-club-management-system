FROM python:3-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade --requirement requirements.txt
COPY . .
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]