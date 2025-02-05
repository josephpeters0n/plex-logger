FROM python:3.12
RUN mkdir /app
ADD bot.py /app
ADD requirements.txt /app
ADD .env.config /app
WORKDIR /app
RUN touch notes.txt
RUN mv .env.config .env
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "bot.py" ]