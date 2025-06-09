build:
	docker build -t hw02 .

typing-local:
	mypy basic.py intermediate.py

typing:
	docker run --rm -v $(PWD)/hw_02 hw02 mypy basic.py intermediate.py

.PHONY: build, typing-local, typing