FROM python:3.7-slim-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    libpq-dev \
    dos2unix \
    gosu \
    && apt-get autoclean \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt /requirements/
RUN pip3 install -r /requirements/base.txt

COPY docker/docker-entrypoint.sh /docker/docker-entrypoint.sh
RUN dos2unix /docker/docker-entrypoint.sh && \
    chmod a+x /docker/docker-entrypoint.sh

ADD . /backend

WORKDIR /backend

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/backend/src
ENV DJANGO_SETTINGS_MODULE='baserow.config.settings.base'

ENTRYPOINT ["/docker/docker-entrypoint.sh"]
CMD ["local"]
