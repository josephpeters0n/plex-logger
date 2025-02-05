FROM python:3.12
RUN mkdir /app
ADD bot.py /app
ADD requirements.txt /app
ADD .env /app
WORKDIR /app
RUN touch notes.txt
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]