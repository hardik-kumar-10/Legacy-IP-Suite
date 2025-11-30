.PHONY: venv install data migrate validate postgres up down clean test

venv:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip

install:
	. .venv/bin/activate && pip install -r requirements.txt

data:
	. .venv/bin/activate && python etl/generate_mock_data.py

migrate:
	. .venv/bin/activate && python etl/migrate.py

validate:
	. .venv/bin/activate && python etl/validate.py

test:
	. .venv/bin/activate && pytest -q

up:
	docker compose up -d

down:
	docker compose down -v

clean:
	rm -rf .venv data/transformed_csv .pytest_cache
