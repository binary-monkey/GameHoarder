FROM python:3

WORKDIR /gamehoarder

ARG LOCAL_SETTINGS="./GameHoarder/local_settings.py"
ARG MYSQL_CONTAINER="mysql_iw13"
ARG REDIS_CONTAINER="redis_iw13"

# copy server files
COPY ./ ./

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# configure connection to database
RUN sed -i -e "s/'HOST': '.*',/'HOST': '${MYSQL_CONTAINER}',/g" ${LOCAL_SETTINGS} && \
    sed -i -e "s/BROKER_URL = 'redis:\/\/.*'/BROKER_URL = 'redis:\/\/${REDIS_CONTAINER}:6379'/g" ${LOCAL_SETTINGS} && \
    sed -i -e "s/CELERY_RESULT_BACKEND = 'redis:\/\/.*'/CELERY_RESULT_BACKEND = 'redis:\/\/${REDIS_CONTAINER}:6379'/g" ${LOCAL_SETTINGS}

# entrypoint
CMD [ "./run.sh", "python", "manage.py", "runserver", "0.0.0.0:8000" ]
