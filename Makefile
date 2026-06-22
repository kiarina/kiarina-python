.PHONY: init update upgrade format lint check test build clean package ci
.DEFAULT_GOAL := check
#--------------------------------------------------
init:
	mise run setup
update:
	uv sync --all-packages --all-extras --all-groups
	uv pip list --outdated
upgrade:
	uv sync --upgrade --all-packages --all-extras --all-groups
clean:
	mise run all:clean
#--------------------------------------------------
format:
	mise run all:format
lint:
	mise run all:lint
test:
	mise run all:test
build:
	mise run all:build
#--------------------------------------------------
package:
	mise run package
check:
	mise run all:check
ci:
	mise run ci
