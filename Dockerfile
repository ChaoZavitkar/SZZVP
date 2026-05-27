FROM python:3.10-slim
WORKDIR /code
COPY code/requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY code /code
CMD ["python", "app.py"]
