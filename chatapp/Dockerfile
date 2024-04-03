FROM python:3.7-alpine
COPY . .
WORKDIR /src
RUN pip install aioredis fastapi uvicorn websockets
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# docker run -d --name chat-a -p 8000:8000 -e HOST_IP=0.0.0.0 chat-app
# docker run -d --rm --name redis -p 6379:6379 redis

