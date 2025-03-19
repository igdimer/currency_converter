run_app:
	docker compose -f docker-compose.dev.yml up -d
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

update_requirements:
	pip-compile && pip-compile requirements.dev.in

upgrade_requirements:
	pip-compile --upgrade && pip-compile requirements.dev.in --upgrade

sync_requirements:
	pip-sync requirements.txt requirements.dev.txt

migrations:
	alembic revision --autogenerate

migrate:
	alembic upgrade head

check:
	isort app
	flake8 app
	mypy app
	pytest
