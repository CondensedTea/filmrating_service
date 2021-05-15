TESTS = tests

VENV ?= .venv
CODE = tests filmrating tools admin

.PHONY: venv
venv:
	python3.9 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

.PHONY: test
test:
	export TESTING='1'; $(VENV)/bin/pytest -v tests

.PHONY: lint
lint:
	$(VENV)/bin/flake8 --jobs 4 --statistics --show-source $(CODE)
	$(VENV)/bin/pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(VENV)/bin/mypy $(CODE)
	$(VENV)/bin/black --skip-string-normalization --check $(CODE)

.PHONY: format
format:
	$(VENV)/bin/isort $(CODE)
	$(VENV)/bin/black --skip-string-normalization $(CODE)
	$(VENV)/bin/autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(VENV)/bin/unify --in-place --recursive $(CODE)

.PHONY: ci
ci:	lint test

.PHONY: db
db:
	$(VENV)/bin/python -m tools.create_db

.PHONY: up
up:
	$(VENV)/bin/uvicorn filmrating.webapp:app

.PHONY: admin
admin:
	export FLASK_APP=admin/webapp.py; $(VENV)/bin/flask run