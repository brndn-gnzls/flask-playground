FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3" ,"-m", "flask", "run", "--host=0.0.0.0"]