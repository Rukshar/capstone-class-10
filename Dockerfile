FROM python:3.7-slim

# set correct timezone for scheduler
ENV TZ Europe/Amsterdam

# set /app as working directory
ENV APP_DIR /app
WORKDIR ${APP_DIR}

# copy the codebase
ADD ./ ${APP_DIR}/

# install requirements
RUN pip install -r requirements.txt

# expose port 5432
EXPOSE 5432

# Run the application when the container launches
CMD ["python", "run_jukebox.py"]