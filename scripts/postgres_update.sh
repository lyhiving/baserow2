#!/bin/sh

chmod +x docker_clone_volume.sh

# Add a check here to verify if the data in the volume needs to be upgraded in the first place

# Clone the volume on which we will do the upgrade
./docker_clone_volume.sh baserow_pgdata baserow_pgdata11

# Remove the old volume, because we will use the original volume name for the upgraded PG data volume
docker volume rm baserow_pgdata

# Run the upgrade
docker run --rm \
	-v baserow_pgdata11:/var/lib/postgresql/11/data \
	-v baserow_pgdata:/var/lib/postgresql/12/data  \
	-e POSTGRES_INITDB_ARGS="--username=${DATABASE_USER:-baserow} --pwfile=<(echo ${DATABASE_PASSWORD:-baserow}) && printf '\nhost all all all md5' >> /var/lib/postgresql/12/data/pg_hba.conf" \
	tianon/postgres-upgrade:11-to-12 \
	--username=${DATABASE_USER:-baserow}