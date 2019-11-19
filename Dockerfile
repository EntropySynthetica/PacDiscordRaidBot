FROM python:3.7-alpine3.9

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN apk add git
RUN python -m pip install -r requirements.txt
RUN git clone https://github.com/Rapptz/discord.py
RUN python3 -m pip install -U /app/discord.py/

ADD .env /app
ADD bot.py /app

CMD [ "python", "/app/bot.py" ]
