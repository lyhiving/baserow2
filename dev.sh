#!/bin/bash

tabname() {
  printf "\e]1;$1\a"
}

print_manual_instructions(){
  COMMAND=$1
  CONTAINER_COMMAND=$2
  echo -e "\nOpen a new tab/terminal and run:"
  echo "    $COMMAND"
}

PRINT_WARNING=true
new_tab() {
  TAB_NAME=$1
  COMMAND=$2
  CONTAINER_COMMAND=$3

  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -x "$(command -v gnome-terminal)" ]; then
      gnome-terminal \
      --tab --title="$TAB_NAME" --working-directory="$(pwd)" -- /bin/bash -c "$COMMAND"
    else
      if $PRINT_WARNING; then
          echo -e "\nWARNING: gnome-terminal is the only currently supported way of opening
          multiple tabs/terminals for linux by this script, add support for your setup!"
          PRINT_WARNING=false
      fi
      print_manual_instructions "$COMMAND" "$CONTAINER_COMMAND"
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript \
        -e "tell application \"Terminal\"" \
        -e "tell application \"System Events\" to keystroke \"t\" using {command down}" \
        -e "do script \"printf '\\\e]1;$TAB_NAME\\\a'; $COMMAND\" in front window" \
        -e "end tell" > /dev/null
  else
    if $PRINT_WARNING; then
        echo -e "\nWARNING: The OS '$OSTYPE' is not supported yet for creating tabs to setup
        baserow's dev environemnt, please add support!"
        PRINT_WARNING=false
    fi
    print_manual_instructions "$COMMAND" "$CONTAINER_COMMAND"
  fi
}

show_help() {
    echo """
./dev.sh starts the baserow development environment and by default attempts to
open terminal tabs which are attached to the running dev containers.

Usage: ./dev.sh [optional start dev commands] [docker-compose commands]

The ./dev.sh Commands are:
dont_attach   : Don't attach to the running dev containers after starting them
restart       : Stop the dev environment first before relaunching
help          : Show this message
"""
}

build=false
up=true
migrate=true
sync_templates=true
while true; do
case "$1" in
    dont_migrate)
        echo "./dev.sh: Automatic migration on startup has been disabled."
        shift
        migrate=false
    ;;
    dont_sync)
        echo "./dev.sh: Automatic template syncing on startup has been disabled."
        shift
        sync_templates=false
    ;;
    dont_attach)
        echo "./dev.sh: Configured to not attach to running dev containers."
        shift
        dont_attach=true
    ;;
    restart)
        echo "./dev.sh: Restarting Dev Environment"
        shift
        down=true
        up=true
    ;;
    stop)
        echo "./dev.sh: Stopping Dev Environment"
        shift
        up=false
        down=true
    ;;
    kill)
        echo "./dev.sh: Killing Dev Environment"
        shift
        up=false
        kill=true
    ;;
    build_only)
        echo "./dev.sh: Only Building Dev Environment (use 'up --build' instead to
        rebuild and up)"
        shift
        build=true
        up=false
    ;;
    help)
        show_help
        exit 0
    ;;
    *)
        break
    ;;
esac
done

CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)
export CURRENT_UID
export CURRENT_GID


if [ "$migrate" = true ] ; then
export MIGRATE_ON_STARTUP="true"
else
# Because of the defaults set in the docker-compose file we need to explicitly turn
# this off as just not setting it will get the default "true" value.
export MIGRATE_ON_STARTUP="false"
fi

if [ "$sync_templates" = true ] ; then
export SYNC_TEMPLATES_ON_STARTUP="true"
else
# Because of the defaults set in the docker-compose file we need to explicitly turn
# this off as just not setting it will get the default "true" value.
export SYNC_TEMPLATES_ON_STARTUP="false"
fi

if [ "$down" = true ] ; then
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
fi

if [ "$kill" = true ] ; then
docker-compose -f docker-compose.yml -f docker-compose.dev.yml kill
fi

if [ "$build" = true ] ; then
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build "$@"
fi

if [ "$up" = true ] ; then
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d "$@"
fi

if [ "$dont_attach" != true ] && [ "$up" = true ] ; then
  new_tab "Backend" \
          "docker logs backend && docker attach backend"

  new_tab "Backend celery" \
          "docker logs celery && docker attach celery"

  new_tab "Web frontend" \
          "docker logs web-frontend && docker attach web-frontend"

  new_tab "Web frontend lint" \
          "docker run -it web-frontend_dev lint-fix"
fi
