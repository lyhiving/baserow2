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

Here are some useful link for that:
[Updating Postgres to Version 12](https://www.postgresql.org/docs/12/upgrading.html)

## How to

First of all, before any update gets applied, you should create a backup of your
PostgreSQL data. Since you are running the docker-compose.yml variant of Baserow
all that data lives in a Docker volume. There are several ways to create a backup.
With this guide you are going to create two backups. One for the Baserow Database
and one of the whole volume (just in case).

### Power down the whole application

In the baserow git folder that you checked out on your server go to the root of that
directory and execute the following

```bash
$ docker-compose down 
```

as any of the subsequent steps need to be taken, when no application and/or user
is accessing the database.

### Backup the volume

There are several ways you could backup a docker volume. For example you could 
follow the official docs [here](https://docs.docker.com/storage/volumes/#backup-restore-or-migrate-data-volumes)

In this guide you are simply going to clone the volume. Just make sure that there is enough
disk space on the server.

The volume you want to backup is most likely called "baserow_pgdata", that is
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

To make it even simpler you can download the following helper script in order to
clone a volume:

```bash
$ curl -o docker_clone_volume.sh https://raw.githubusercontent.com/gdiepen/docker-convenience-scripts/master/docker_clone_volume.sh
$ chmod +x docker_clone_volume.sh
```

Now clone the baserow_pgdata volume (in case your volume is named differently, please
update the command accordingly):

```bash
$ ./docker_clone_volume.sh baserow_pgdata baserow_pgdata_backup
```

If any of the following steps fail, you can simply clone the volume back into the previous volume
and be good to go.

### Backup the Baserow PostgreSQL database

One of the recommended ways to move to a newer version of PostgreSQL is
dumping the old database and restoring that dump in the new version. You are going
to make use of baserows internal backup and restore functionality in order to do
so.

```bash
$ mkdir ~/baserow_backups
# The folder must be the same UID:GID as the user running inside the container, which
# for the local env is 9999:9999, for the dev env it is 1000:1000 or your own UID:GID
# when using ./dev.sh
$ sudo chown 9999:9999 ~/baserow_backups/ 
$ docker-compose run -e PGPASSWORD=baserow -v ~/baserow_backups:/baserow/backups backend manage backup_baserow -h db -d baserow -U baserow -f /baserow/backups/baserow_backup.tar.gz 
$ docker-compose down
# You want the new db container running PG12 to initialize it's own datadir, therefore
# you have to remove the old volume
$ docker volume rm baserow_pgdata
# ~/baserow_backups/ now contains your Baserow backup.
```

### Pull the latest changes from the repository and build

```bash
$ git pull && git fetch
# It might be a good idea to checkout the tag of the release
$ git checkout 1.6.0 
$ docker-compose build
```

### Restore the Baserow database

```bash
$ docker-compose run -e PGPASSWORD=baserow -v ~/baserow_backups/:/baserow/backups/ backend manage restore_baserow -h db -d baserow -U baserow -f /baserow/backups/baserow_backup.tar.gz
```

### Boot up Baserow

```bash
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
$ ./docker_clone_volume.sh baserow_pgdata_backup baserow_pgdata
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
$ rm -rf ~/baserow_backups
$ docker volume rm baserow_pgdata_backup
$ rm docker_clone_volume.sh
```