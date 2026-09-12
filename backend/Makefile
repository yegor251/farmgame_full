PYTHON := python3.13
VENV := .venv

.PHONY: install lint typecheck test run run-deposit-watcher run-withdraw-processor

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"

lint:
	$(VENV)/bin/ruff check app tests

typecheck:
	$(VENV)/bin/mypy app

test:
	$(VENV)/bin/pytest

init:
	cp .env.example .env

run:
	$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

run-deposit:
	$(VENV)/bin/python -m app.crypto.run_deposit_watcher

run-withdraw:
	$(VENV)/bin/python -m app.crypto.run_withdraw_processor
