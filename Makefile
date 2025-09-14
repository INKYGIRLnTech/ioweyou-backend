PYTHON := .venv/bin/python
PIP := .venv/bin/pip
UVICORN := .venv/bin/uvicorn

.PHONY: venv install run test migrate upgrade downgrade backfill

venv:
	python3 -m venv .venv
	$(PYTHON) -m pip install -U pip

install: venv
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTHON) -m pytest -q

migrate:
	$(PYTHON) -m alembic upgrade head

upgrade:
	$(PYTHON) -m alembic upgrade head

downgrade:
	$(PYTHON) -m alembic downgrade -1

backfill:
	$(PYTHON) scripts/backfill_passwords.py

