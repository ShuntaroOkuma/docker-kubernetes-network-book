FROM python:3.12.3-alpine
ADD app.py /app/
WORKDIR /app/
RUN pip install flask
RUN apk add curl
CMD ["python", "app.py"]