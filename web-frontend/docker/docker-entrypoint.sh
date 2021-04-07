#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# http://stackoverflow.com/questions/19622198/what-does-set-e-mean-in-a-bash-script
set -e

CURRENT_UID=${CURRENT_UID:-9999}
CURRENT_GID=${CURRENT_GID:-9999}
# Create a user either with the provided uid or a default non-root uid
groupadd -g "$CURRENT_GID" baserow_docker_group || echo "Group $CURRENT_GID already exists, not creating."
useradd --shell /bin/bash -u "$CURRENT_UID" -g "$CURRENT_GID" -o -c "" -m baserow_docker_user  || echo "User $CURRENT_UID already exists, not creating."
export HOME=/home/baserow_docker_user

# Fixup the working directory as it was probably built in the docker image as root but
# the application user needs access.
#chown "$CURRENT_UID":"$CURRENT_GID" -R .

exec_as_correct_user(){
  exec gosu "$CURRENT_UID" "$@"
}
# Define help message
show_help() {
    echo """
Usage: docker run <imagename> COMMAND
Commands
dev      : Start a normal nuxt development server
local    : Start a non-dev prod ready nuxt server
lint     : Run the linting
lint-fix : Run eslint fix
bash     : Start a bash shell
help     : Show this message
"""
}


# Run
case "$1" in
    dev)
        CMD="yarn run dev"
        echo "$CMD"
        echo "history -s $CMD; $CMD" > /tmp/initfile
        chown "$CURRENT_UID":"$CURRENT_GID" /tmp/initfile
        exec_as_correct_user bash --init-file /tmp/initfile
    ;;
    local)
      exec_as_correct_user yarn run start
    ;;
    lint)
      exec_as_correct_user make lint
    ;;
    lint-fix)
      exec_as_correct_user yarn run eslint --fix
    ;;
    bash)
      exec_as_correct_user /bin/bash "${@:2}"
    ;;
    *)
      show_help
      exit 1
    ;;
esac