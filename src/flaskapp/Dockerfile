FROM python:3.7-slim

# set correct timezone for scheduler
ENV TZ Europe/Amsterdam
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=docker

# set /app as working directory
ENV APP_DIR /app
WORKDIR ${APP_DIR}

# copy the codebase
ADD ./ ${APP_DIR}/

# install requirements
RUN pip install -r requirements.txt

# expose port 8080 to access the app
EXPOSE 8080

# Run the application when the container launches with gevent
# CMD ["python", "serve_gevent.py"]

# Run with gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4" , "--log-level", "debug", "src.flaskapp.wsgi:app"]


