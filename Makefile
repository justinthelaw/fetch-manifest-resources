.DEFAULT_GOAL := build

.PHONY: all

build:
	docker build -t fetch-resources:latest .

test: build
	docker run --rm -v ${PWD}/tests:/work -it fetch-resources:latest
