FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN apt update && apt install -y cron \
    && rm -rf /var/lib/apt/lists/*

RUN chmod a+x ./docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]