#!/bin/bash

tabname() {
  printf "\e]1;$1\a"
}

print_manual_instructions(){
  COMMAND=$1
  CONTAINER_COMMAND=$2
  echo -e "\nOpen a new tab/terminal and run:"
  echo "    $COMMAND"
  echo "Then inside the container run:"
  echo "    $CONTAINER_COMMAND"
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
./start_dev.sh starts the baserow development environment and by default attempts to
open terminal tabs which are attached to the running dev containers.

Usage: ./start_dev.sh [optional start dev commands] [docker-compose commands]

The ./start_dev.sh Commands are:
dont_attach   : Don't attach to the running dev containers after starting them
restart       : Stop the dev environment first before relaunching
help          : Show this message
"""
}

while true; do
case "$1" in
    dont_migrate)
        echo "./start_dev: Automatic migration on startup has been disabled."
        shift
        export DONT_MIGRATE="true"
    ;;
    dont_attach)
        echo "./start_dev: Configured to not attach to running dev containers."
        shift
        dont_attach=true
    ;;
    restart)
        echo "./start_dev: Restarting Dev Environment"
        shift
        restart=true
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

if [ "$restart" = true ] ; then
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
fi

docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d "$@"

if [ "$dont_attach" != true ] ; then
  new_tab "Backend" \
          "docker logs backend && docker attach backend"

  new_tab "Backend celery" \
          "docker logs celery && docker attach celery"

  new_tab "Web frontend" \
          "docker logs web-frontend && docker attach web-frontend"

  new_tab "Web frontend eslint" \
          "docker exec -it web-frontend eslint-fix"
fi
