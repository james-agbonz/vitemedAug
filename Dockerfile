FROM youyinnn/base_python:1.0.2

ARG APP_HOME

COPY ./backend/dev /backend/dev
COPY ./backend/requirements.txt /backend/requirements.txt

RUN pip install /backend/dev

WORKDIR /app
COPY ${APP_HOME} /app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
# flask run --host=0.0.0.0 --port=5000
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]