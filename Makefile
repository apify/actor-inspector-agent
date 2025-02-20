.PHONY: clean install-dev lint type-check check-code format

DIRS_WITH_CODE = src

clean:
	rm -rf .venv .mypy_cache .pytest_cache .ruff_cache __pycache__

install-dev:
	cd $(DIRS_WITH_CODE) && uv sync --frozen && uv run pre-commit install && cd ..

lint:
	uv run ruff check $(DIRS_WITH_CODE)

type-check:
	uv run mypy $(DIRS_WITH_CODE)

check-code: lint type-check

format:
	uv run ruff check --fix $(DIRS_WITH_CODE)
	uv run ruff format $(DIRS_WITH_CODE)

docker-build:
	docker build --tag dataset-query-engine --file .actor/Dockerfile .

docker-run:
	echo "Stopping and removing the container"
	docker stop dataset-query-engine 2> /dev/null || true
	docker rm dataset-query-engine 2> /dev/null || true

	echo "Running the container"
	docker run --name dataset-query-engine -it -p 4321:4321 dataset-query-engine

make build-run:
	make docker-build
	make docker-run

pydantic-model:
	datamodel-codegen --input .actor/input_schema.json --output $(DIRS_WITH_CODE)/input_model.py  --input-file-type jsonschema  --field-constraints  --enum-field-as-literal all

pytest:
	uv run -C $(DIRS_WITH_CODE) pytest --with-integration --vcr-record=none