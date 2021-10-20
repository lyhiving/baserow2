FROM gitpod/workspace-postgres

# We want to install Redis version 5.
RUN sudo add-apt-repository ppa:chris-lea/redis-server
RUN sudo apt-get update && \
    sudo apt-get install -y redis-server && \
    sudo rm -rf /var/lib/apt/lists/* \
RUN systemctl start redis-server.service
ENV REDIS_HOST=localhost

USER gitpod

ENV DATABASE_HOST=localhost
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$PYTHONPATH:/workspace/baserow/backend/src:/workspace/baserow/premium/backend/src
ENV DJANGO_SETTINGS_MODULE='baserow.config.settings.dev'
