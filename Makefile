run:
	@ python -m shellgpt.main

init:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

.PHONY: init freeze test
