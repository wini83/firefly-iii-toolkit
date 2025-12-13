dev:
	PYTHONPATH=src uv run uvicorn main:app --reload --app-dir src

test:
	uv run pytest