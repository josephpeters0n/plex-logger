FROM python:3.12
RUN mkdir /app
ADD bot.py /app
ADD requirements.txt /app
ADD config.env /app
WORKDIR /app
RUN touch notes.txt
RUN if [ -f config.env ] && [ ! -f .env ]; then mv config.env .env; fi
RUN if [ -f config.env ] && [ -f .env ]; then rm config.env; fi
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]