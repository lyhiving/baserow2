FROM gitpod/workspace-postgres

# We want to install Redis version 5.
RUN sudo add-apt-repository ppa:chris-lea/redis-server
RUN sudo apt-get update && \
    sudo apt-get install -y redis-server && \
    sudo rm -rf /var/lib/apt/lists/*

USER gitpod
