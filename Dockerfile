FROM python:3.7-alpine3.10

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt

ADD .env /app
ADD bot.py /app

CMD [ "python", "/app/bot.py" ]
