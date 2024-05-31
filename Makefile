run:
	@ python -m shellgpt.main

init:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

build:
	hatch build

.PHONY: init freeze test build
