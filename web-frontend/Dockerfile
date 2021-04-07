FROM node:10

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    dos2unix \
    gosu \
    && apt-get autoclean \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

COPY package.json yarn.lock /web-frontend/

WORKDIR /web-frontend

RUN yarn install --production=true

COPY docker/docker-entrypoint.sh /docker/docker-entrypoint.sh
RUN dos2unix /docker/docker-entrypoint.sh && \
    chmod a+x /docker/docker-entrypoint.sh

ADD . /web-frontend

RUN yarn run build

ENTRYPOINT ["/docker/docker-entrypoint.sh"]
CMD ["local"]

