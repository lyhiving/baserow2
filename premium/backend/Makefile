lint:
	flake8 src tests && black . --check  || exit;

format:
	black . exit;

test:
	pytest tests || exit;
