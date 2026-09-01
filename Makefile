.PHONY: install run test import

install:
	python -m pip install -r requirements.txt pytest httpx

run:
	python -m uvicorn backend.app:app --reload

test:
	python -m pytest -q

import:
	python scripts/import_csv.py database/exemplo_respostas.csv

