FROM gitpod/workspace-postgres

# Create a PostgreSQL baserow database and user.
RUN sudo -u postgres psql << EOF
    create database baserow;
    create user baserow with encrypted password 'baserow';
    grant all privileges on database baserow to baserow;
EOF
ENV DATABASE_HOST localhost

# We want to install Redis version 5.
RUN add-apt-repository ppa:chris-lea/redis-server
RUN sudo apt-get update && \
    sudo apt-get install -y redis-server && \
    sudo rm -rf /var/lib/apt/lists/*

USER gitpod
