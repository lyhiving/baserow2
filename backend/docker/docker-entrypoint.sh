#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# http://stackoverflow.com/questions/19622198/what-does-set-e-mean-in-a-bash-script
set -e

CURRENT_UID=${CURRENT_UID:-9999}
CURRENT_GID=${CURRENT_GID:-9999}
groupadd -g "$CURRENT_GID" baserow_docker_group || echo "Group $CURRENT_GID already exists, not creating."
useradd --shell /bin/bash -u "$CURRENT_UID" -g "$CURRENT_GID" -o -c "" -m baserow_docker_user  || echo "User $CURRENT_UID already exists, not creating."
export HOME=/home/baserow_docker_user

# Fixup the working directory as it was probably built in the docker image as root but
# the application user needs access.
#chown "$CURRENT_UID":"$CURRENT_GID" -R .

# Check if the required PostgreSQL environment variables are set

# Used by docker-entrypoint.sh to start the dev server
# If not configured you'll receive this: CommandError: "0.0.0.0:" is not a valid port number or address:port pair.
PORT="${PORT:-8000}"
DATABASE_USER="${DATABASE_USER:-postgres}"
DATABASE_HOST="${DATABASE_HOST:-db}"
DATABASE_PORT="${DATABASE_PORT:-5432}"


postgres_ready() {
python << END
import sys
import psycopg2
try:
    psycopg2.connect(
        dbname="${DATABASE_NAME}",
        user="${DATABASE_USER}",
        password="${DATABASE_PASSWORD}",
        host="${DATABASE_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

wait_for_postgres() {
[ -z "$DATABASE_NAME" ] && echo "ERROR: Need to set DATABASE_NAME" && exit 1;
[ -z "$DATABASE_PASSWORD" ] && echo "ERROR: Need to set DATABASE_PASSWORD" && exit 1;

until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'
}


# Define help message
show_help() {
    echo """
Usage: docker run <imagename> COMMAND
Commands
dev       : Start a normal Django development server
bash      : Start a bash shell
manage    : Start manage.py
python    : Run a python command
shell     : Start a Django Python shell
celery    : Run celery
celery-dev: Run a hot-reloading dev version of celery
lint:     : Run the linting
help      : Show this message
"""
}

exec_as_correct_user(){
  exec gosu "$CURRENT_UID" "$@"
}

# Run
case "$1" in
    dev)
        wait_for_postgres
        [ -z "$DONT_MIGRATE" ] && python src/baserow/manage.py migrate
        echo "Running Development Server on 0.0.0.0:${PORT}"
        echo "Press CTRL-p CTRL-q to close this session without stopping the container."
        CMD="python src/baserow/manage.py runserver 0.0.0.0:${PORT}"
        echo "$CMD"
        # The below command lets devs attach to this container, press ctrl-c and only
        # the server will stop. Additionally they will be able to use bash history to
        # re-run the containers run server command after they have done what they want.
        echo "history -s $CMD; $CMD" > /tmp/initfile
        chown "$CURRENT_UID":"$CURRENT_GID" /tmp/initfile
        exec_as_correct_user bash --init-file /tmp/initfile
    ;;
    local)
        wait_for_postgres
        [ -z "$DONT_MIGRATE" ] && python src/baserow/manage.py migrate
        exec_as_correct_user gunicorn --workers=3 -b 0.0.0.0:"${PORT}" -k uvicorn.workers.UvicornWorker baserow.config.asgi:application
    ;;
    bash)
        exec_as_correct_user /bin/bash "${@:2}"
    ;;
    manage)
        exec_as_correct_user python src/baserow/manage.py "${@:2}"
    ;;
    python)
        exec_as_correct_user python "${@:2}"
    ;;
    shell)
        exec_as_correct_user python manage.py shell
    ;;
    lint)
        exec_as_correct_user make lint
    ;;
    celery)
        exec_as_correct_user celery -A baserow worker -l INFO
    ;;
    celery-dev)
        exec_as_correct_user watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A baserow worker -l INFO
    ;;
    *)
        show_help
        exit 1
    ;;
esac