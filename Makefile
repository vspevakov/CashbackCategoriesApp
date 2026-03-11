IMAGE_NAME := cashback-app
TEST_DATA_DIR := .tmp/test_data
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: docker-build docker-test prepare-test-data setup-venv run-test-data

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-test: docker-build
	docker run --rm -e PYTHONPATH=/app $(IMAGE_NAME) pytest

setup-venv:
	python3 -m venv $(VENV_DIR)
	$(PYTHON) -m pip install -r requirements.txt

prepare-test-data:
	mkdir -p $(TEST_DATA_DIR)
	cp tests/fixtures/cashback_data.json $(TEST_DATA_DIR)/cashback_data.json
	cp tests/fixtures/categories.json $(TEST_DATA_DIR)/categories.json

run-test-data: setup-venv prepare-test-data
	TEST_DATA_DIR=$(TEST_DATA_DIR) $(PYTHON) -m uvicorn app.main:app --reload
