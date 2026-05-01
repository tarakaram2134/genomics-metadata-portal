PYTHON := .venv/bin/python
PIP := .venv/bin/pip

install:
	$(PIP) install -r requirements-dev.txt

freeze:
	$(PIP) freeze > requirements-dev-lock.txt

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f postgres

test:
	$(PYTHON) -m pytest

smoke:
	$(PYTHON) -m scripts.smoke_test

format:
	$(PYTHON) -m black app scripts tests streamlit_app

lint:
	$(PYTHON) -m ruff check app scripts tests streamlit_app

run:
	$(PYTHON) -m streamlit run streamlit_app/Home.py