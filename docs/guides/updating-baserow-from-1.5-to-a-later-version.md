# Updating Baserow Docker from version 1.5 to a later version

In case you are self hosting Baserow via our docker-compose.yml file and are 
upgrading from version 1.5 or prior to 1.6 or later you need to upgrade your PostgreSQL datadir.
With the release of Baserow 1.6 we are upgrading the minimum required version of 
PostgreSQL from 11 to 12.
In order for PostgreSQL to work correctly after the update some manual steps are needed.

> If you are running Baserow on a VM it is strongly advised to create 
> a snapshot of the whole machine. In case of any failure 
> you will still be able to boot up a VM with a working Baserow installation. Before creating
> the snapshot please power down Baserow.

The following only covers the case, that you are using Baserows provided
docker-compose.yml file in order to run Baserow on your server. If you have a custom
setup you need to take care of updating PostgreSQL and the PostgreSQL datadir to version 12
by yourself (please be sure to make a backup before you do any updates).

Here is a useful link for that:
[Updating Postgres to Version 12](https://www.postgresql.org/docs/12/upgrading.html)

## How to

Before you upgrade the Baserow PostgreSQL database, you need to rename the current
docker volume which holds the PostgreSQL data. With this guide you are going to create
a new docker volume with a PostgreSQL 12 compatible data directory. This new volume is going
to be named the same as the current volume.

### Power down the whole application

In the baserow git folder that you checked out on your server go to the root of that
directory and execute the following

```bash
$ docker-compose down 
```

as any of the subsequent steps need to be taken, when no application and/or user
is accessing the database.

### Rename the volume

There is not a straightforward way to rename a docker volume, which is why you
are going to clone the volume to a new volume and remove the old volume.

The volume you want to rename is most likely called "baserow_pgdata", that is
if you haven't changed anything in the docker-compose.yml file. To be sure you can use

```bash
$ docker volume ls
```

to get a list of all the available volumes.

> In case you are running a version of Baserow prior to 1.2 you need to be aware that there 
> will be no "baserow_pgdata" volume, as the "named volume" was introduced in Baserow 1.2.
> Therefore you need to inspect the "db" container to find out which volume belongs to it.
> Run the following: docker inspect -f '{{ .Mounts }}' db
> Copy the volume ID and use that in the subsequent commands instead of "baserow_pgdata".

Download the following helper script in order to clone a volume:

```bash
$ curl -o docker_clone_volume.sh https://raw.githubusercontent.com/gdiepen/docker-convenience-scripts/master/docker_clone_volume.sh
$ chmod +x docker_clone_volume.sh
```

Now clone the baserow_pgdata volume (in case your volume is named differently, please
update the command accordingly):

```bash
$ ./docker_clone_volume.sh baserow_pgdata baserow_pgdata11

# Only remove the volume if the previous command succeeded
$ docker volume rm baserow_pgdata
```

If any of the following steps fail, you can simply clone the volume back 
and be good to go.

### Upgrade the Baserow PostgreSQL database

One of the recommended ways to move to a newer version of PostgreSQL is
using PostgreSQLs own "pg_upgrade" utility. There is a Github
repository that provides Docker images for migrating PostgreSQL datadirs 
from one version to another, utilizing "pg_upgrade". You can find it [here](https://github.com/tianon/docker-postgres-upgrade).
With the following command you are going to make use of one of their Docker images.

```bash
docker run --rm \
	-v baserow_pgdata11:/var/lib/postgresql/11/data \
	-v baserow_pgdata:/var/lib/postgresql/12/data  \
	-e POSTGRES_INITDB_ARGS="--username=${DATABASE_USER:-baserow} --pwfile=<(echo ${DATABASE_PASSWORD:-baserow}) && printf '\nhost all all all md5' >> /var/lib/postgresql/12/data/pg_hba.conf" \
	tianon/postgres-upgrade:11-to-12 \
	--username=${DATABASE_USER:-baserow}
```

### Pull the latest changes from the repository, build and boot the application

```bash
$ git pull && git fetch
# It might be a good idea to checkout the tag of the release you are upgrading to.
$ git checkout X.X.X 
$ docker-compose build
$ docker-compose up -d
```

You should be able to go to your login page and start using Baserow again.


## Rollback

In case any of the previous steps fail, you can go back to the previous
version of Baserow by cloning your backup volume back into the original volume,
checkout the previous version of Baserow, build the images again and start
the containers.

### Checkout previous version of Baserow


```bash
$ docker-compose down
$ git checkout 1.5.0
```

### Clone the backup volume

At this point the uncorrupted PostgreSQL data lives in the backup volume
created in a step above. You do the inverse now in order to use that data
with the docker-compose.yml file:

```bash
$ docker volume rm baserow_pgdata
$ ./docker_clone_volume.sh baserow_pgdata11 baserow_pgdata
```

### Rebuild the images and start the containers

Once the data is back in its original place, you can rebuild the images
and start up Baserow:

```bash
$ docker-compose build
$ docker-compose up -d
```

## Clean-Up

If the update was successful or you rolled back you can delete the backup
volume, backup folder and the clone utility.

```bash
$ docker volume rm baserow_pgdata11
$ rm docker_clone_volume.sh
```
