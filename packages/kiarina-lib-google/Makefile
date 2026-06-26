.PHONY: format lint test build clean check
.DEFAULT_GOAL := check
# Package-scoped tasks. `mise run` always executes from the repository root and
# resolves the target package from this directory via `package:current`, so no
# package name needs to be passed explicitly.
format:
	mise run format
lint:
	mise run lint
test:
	mise run test
build:
	mise run build
clean:
	mise run clean
check:
	mise run format
	mise run lint
	mise run test --coverage
