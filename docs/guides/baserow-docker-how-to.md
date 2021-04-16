# Baserow Docker How To

Find below a list of common operations and problems when working with Baserow's docker 
environment. 

## View the logs
```bash
$ docker-compose logs 
```

## Run Baserow alongside existing services like a local postgresql

Baserow's docker-compose files will automatically bind to the following ports on your
machine. If you already have applications or services using those ports the Baserow 
service which uses that port by default will crash like so:
```bash
Creating network "baserow_local" with driver "bridge"
Creating db ... 
Creating db    ... error
Creating redis ... 
WARNING: Host is already in use by another container

Creating mjml  ... done
Creating redis ... done

ERROR: for db  Cannot start service db: driver failed programming external connectivity on endpoint db (...): Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use
ERROR: Encountered errors while bringing up the project.
```
To fix this you can change which ports Baserow will use by setting the
corresponding environment variable shown below: 

- Port 5432 for postgres, change using `POSTGRES_PORT`
- Port 6379 for redis, change using `REDIS_PORT`
- Port 28101 for mjml, change using `MJML_PORT`
- Port 8000 for the baserow backend server, change using `BACKEND_PORT`
- Port 3000 for the baserow web-frontend server, change using `WEB_FRONTEND_PORT`

Below is an example on how to set these variables in bash:
```bash
$ POSTGRES_PORT=5555 REDIS_PORT=6666 MJML_PORT=7777 docker-compose up 
$ # or using dev.sh
$ POSTGRES_PORT=5555 REDIS_PORT=6666 MJML_PORT=7777 ./dev.sh
```

## Change what User the Baserow containers run as in development

When running the dev env you can set the `UID` and `GID` environment variables when 
build and then running to change the user id and group id for the following baserow containers:

- backend
- celery
- web-frontend

> Remember you need to re-build the images if you change these variables or run the
> `./dev.sh` on a new user as Baserow's images build with file permissions set to the
> given UID and GID.

When using `./dev.sh` it will automatically set `UID` and `GID` to the id's of the
user running the command for you. 

## Disable automatic migration

You can disable automatic migration by setting the MIGRATE_ON_STARTUP environment
variable to `false` (or any value which is not `true`) like so:

```bash
$ MIGRATE_ON_STARTUP=false docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
$ # Or instead using ./dev.sh 
$ ./dev.sh dont_migrate  # dev.sh supports this as an explicit argument.
$ MIGRATE_ON_STARTUP=false ./dev.sh # or dev.sh will pass through whatever you have set. 
```

## Run a one off migration

See [baserow's docker usage](../getting-started/docker-usage.md) for the full
details on what commands and environment variables baserow's docker-compose and docker
image's support.

```bash
# Run a one off dev container using the backend image which supports the "manage" command like so:
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml run backend manage migrate
$ # Or instead using ./dev.sh 
$ ./dev.sh run backend manage migrate
```

## Disable automatic baserow template syncing

You can disable automatic baserow template syncing by setting the
SYNC_TEMPLATES_ON_STARTUP environment variable to `false` (or any value which is
not `true`) like so:

```bash
$ SYNC_TEMPLATES_ON_STARTUP=false docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
$ # Or instead using ./dev.sh 
$ ./dev.sh dont_sync # dev.sh supports this as an explicit argument.
$ SYNC_TEMPLATES_ON_STARTUP=false ./dev.sh # or dev.sh it will pass through whatever you have set. 
```

## Run a one off management command

See [baserow's docker usage](../getting-started/docker-usage.md) for the full
details on what commands and environment variables baserow's docker-compose and docker
image's support.

```bash
# Run a one off dev container using the backend image which supports the "manage" command like so:
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml run backend manage sync_templates 
$ # Or instead using ./dev.sh 
$ ./dev.sh run backend manage sync_templates 
```
