FROM python:3.7-alpine3.10

WORKDIR /app

ADD requirements.txt /app/requirements.txt
#Added the following line so pylint builds correctly in the Apline container. 
RUN python3 -c 'import sys; f = open("/usr/local/lib/python3.7/site-packages/_manylinux.py", "w"); f.write("manylinux1_compatible = True"); f.close()'
RUN python -m pip install -r requirements.txt

ADD .env /app
ADD bot.py /app

CMD [ "python", "-u", "/app/bot.py" ]
