FROM python:3.10
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]