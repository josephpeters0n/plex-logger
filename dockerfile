FROM python:3.12
RUN mkdir /app
ADD bot.py /app
ADD requirements.txt /app
ADD .env /app
ADD notes.txt /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD [ "bot.py"]