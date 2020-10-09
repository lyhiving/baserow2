#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# http://stackoverflow.com/questions/19622198/what-does-set-e-mean-in-a-bash-script
set -e

# Check if the required PostgreSQL environment variables are set

# Used by docker-entrypoint.sh to start the dev server
# If not configured you'll receive this: CommandError: "0.0.0.0:" is not a valid port number or address:port pair.
[ -z "$PORT" ] && echo "ERROR: Need to set PORT. E.g.: 8000" && exit 1;

[ -z "$POSTGRES_DB" ] && echo "ERROR: Need to set POSTGRES_DB_NAME" && exit 1;
[ -z "$POSTGRES_USER" ] && echo "ERROR: Need to set POSTGRES_USER" && exit 1;
[ -z "$POSTGRES_PASSWORD" ] && echo "ERROR: Need to set POSTGRES_PASSWORD" && exit 1;
[ -z "$DATABASE_PORT" ] && echo "ERROR: Need to set POSTGRES_PASSWORD" && exit 1;


# Define help message
show_help() {
    echo """
Usage: docker run <imagename> COMMAND

Commands

dev      : Start a normal Django development server
bash     : Start a bash shell
manage   : Start manage.py
setup_db : Setup the initial database. Configure \$POSTGRES_DB_NAME in docker-compose.yml
lint     : Run pylint
python   : Run a python command
shell    : Start a Django Python shell
uwsgi    : Run uwsgi server
help     : Show this message
"""
}

write_uwsgi() {
    echo "Generating uwsgi config file..."
    snippet="import os;
import sys;
import jinja2;
sys.stdout.write(jinja2.Template(sys.stdin.read()).render(env=os.environ))"

    cat /deployment/uwsgi.ini | python -c "${snippet}" > /uwsgi.ini
}

# Run
case "$1" in
    dev)
        echo "Running Development Server on 0.0.0.0:${PORT}"
        wait-for db:5432 -- python src/baserow/manage.py runserver 0.0.0.0:${PORT}
    ;;
    bash)
        /bin/bash "${@:2}"
    ;;
    manage)
        python manage.py "${@:2}"
    ;;
    setup_db)
        psql -h $DATABASE_PORT -U $POSTGRES_USER -c "CREATE DATABASE $POSTGRES_DB_NAME"
        python manage.py migrate
    ;;
    lint)
        pylint "${@:2}"
    ;;
    python)
        python "${@:2}"
    ;;
    shell)
        python manage.py shell_plus
    ;;
    uwsgi)
        echo "Running App (uWSGI)..."
        write_uwsgi
        uwsgi --ini /uwsgi.ini
    ;;
    web)
        echo "Starting Nginx ..."
        wait-for hasura:8080
    ;;
    celery)
        echo "Starting Celery worker ..."
        wait-for redis:6379 && wait-for app:8000 -- celery -A app_creator worker -l info -n worker1@%h --pidfile=
    ;;
    beat)
        echo "Starting Celery beat scheduler ..."
        wait-for redis:6379 && wait-for app:8000 -- celery -A app_creator beat -l info --pidfile=
    ;;
    flower)
        echo "Starting Flower, a web interface for Celery ..."
        wait-for redis:6379 && wait-for app:8000 -- celery flower -A app_creator --broker=$CELERY_BROKER_URL --auto_refresh=True
    ;;
    *)
        show_help
    ;;
esac
