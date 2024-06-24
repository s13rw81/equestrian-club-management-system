FROM python:3-slim
WORKDIR /app
COPY . .
RUN pip install pip install --upgrade --requirement requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]