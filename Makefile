PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

.PHONY: install run test lint clean

install:
	chmod +x scripts/install.sh
	./scripts/install.sh

run:
	cd backend && $(UVICORN) main:app --host 0.0.0.0 --port 8000 --reload

test:
	cd backend && $(PYTHON) -m compileall .
	$(PYTHON) scripts/smoke_test.py

lint:
	cd backend && $(PYTHON) -m compileall .
	$(PYTHON) -m compileall agent

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
