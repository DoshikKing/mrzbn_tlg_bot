FROM python:3.13.1
WORKDIR /app
COPY requirements.txt /app/
COPY settings.ini /app/
RUN pip install -r requirements.txt
COPY . /app
CMD ["python", "main.py", "--settings", "settings.ini"]