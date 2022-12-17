test:
	poetry run pytest

fmt:
	poetry run black .

.PHONY: test fmt
