## Dev.sh

By default `dev.sh` will start the dev env, attach into the running containers and make
sure the containers are running as your actual user.

### Example Dev.sh usage:

```bash
$ ./dev.sh # same as the up command above but also ensures the containers run as the running user!
$ ./dev.sh --build # ups and rebuilds
$ ./dev.sh restart # stops and then ups
$ ./dev.sh restart --build # stops, builds, ups
$ ./dev.sh build_only # just builds
$ ./dev.sh dont_attach # does not create tabs and attach to the containers at the end
$ ./dev.sh dont_attach restart --build # You can combine multiple arguments like so
$ ./dev.sh dont_migrate # ups but doesn't migrate automatically on startup
$ ./dev.sh dont_migrate dont_sync dont_attach restart --build # even more flags!
$ ./dev.sh run backend manage migrate
# Any commands found after the last `./dev.sh` command will be passed to the `docker-compose up` call made by dev.sh
# This lets you say do --build on the end or any other docker-compose commands using dev.sh!
$ ./dev.sh restart {EXTRA_COMMANDS_PASSED_TO_UP}  
$ ./dev.sh stop # stops
$ ./dev.sh kill # kills (the old stop_dev.sh)
# Bind to different ports on the host manage incase you are already running them and they clash! (also works with just docker-compose up)
$ POSTGRES_PORT=5555 REDIS_PORT=6666 MJML_PORT=7777 ./dev.sh
```

### Why Dev.sh ensures the containers run as you

In dev mode Baserow's source control directories are mounted from your local git repo
into the containers. By mounting these the containers will see source code changes and
automatically rebuild. However, if the containers are not running as your actual user
then the containers might accidentally change the ownership or create files owned by the
user running inside the container. So by running the containers as your user there is no
chance that your source control directories will have file ownership problems.
Additionally, it
is [best practice](https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b)
to not run Docker containers as the default root user.
