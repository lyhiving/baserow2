install-dependencies:
	apt-get install -y --no-install-recommends \
	wget \
	lsb-release \
	gnupg2 \
	&& sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
	&& wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
	apt-get update && apt-get install -y libpq-dev postgresql-client-12
	pip install -r requirements/base.txt

install-dev-dependencies:
	pip install -r requirements/dev.txt

lint:
	flake8 src tests plugins && black . --check || exit;

lint-python: lint

format:
	black . || exit;

test:
	pytest || exit;
