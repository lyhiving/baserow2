#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# http://stackoverflow.com/questions/19622198/what-does-set-e-mean-in-a-bash-script
set -e

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
        # The below command lets devs attach to this container, press ctrl-c and only
        # the server will stop. Additionally they will be able to use bash history to
        # re-run the containers run server command after they have done what they want.
        exec bash --init-file <(echo "history -s $CMD; $CMD")
    ;;
    local)
      exec yarn run start
    ;;
    lint)
      exec make lint
    ;;
    lint-fix)
      CMD="yarn run eslint --fix"
      echo "$CMD"
      exec bash --init-file <(echo "history -s $CMD; $CMD")
    ;;
    bash)
      exec /bin/bash "${@:2}"
    ;;
    *)
      show_help
      exit 1
    ;;
esac