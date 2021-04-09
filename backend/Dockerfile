FROM python:3.7-slim-buster

ARG UID
ENV UID=${UID:-9999}
ARG GID
ENV GID=${GID:-9999}

RUN groupadd -g $GID baserow_docker_group && \
    useradd --shell /bin/bash -u $UID -g $GID -o -c "" -m baserow_docker_user

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    libpq-dev \
    dos2unix \
    tini \
    && apt-get autoclean \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

USER $UID:$GID
# Ensure installed python binaries are on the path as expected.
ENV PATH $PATH:/home/baserow_docker_user/.local/bin

ADD --chown=$UID:$GID requirements/base.txt /requirements/
RUN pip3 install -r /requirements/base.txt

ADD --chown=$UID:$GID . /backend

WORKDIR /backend

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/backend/src
ENV DJANGO_SETTINGS_MODULE='baserow.config.settings.base'

RUN dos2unix /backend/docker/docker-entrypoint.sh && \
    chmod a+x /backend/docker/docker-entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/backend/docker/docker-entrypoint.sh"]
CMD ["local"]
