.DEFAULT_GOAL := test

build:
				docker build -t fetch-resources:latest .
.PHONY:build

test: build
				docker run --rm -v ${PWD}/tests:/work -it fetch-resources:latest
.PHONY:test