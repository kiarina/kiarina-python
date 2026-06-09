.DEFAULT_TARGET: check

init:
	mise run setup
update:
	uv sync --all-packages --all-extras --all-groups
	uv pip list --outdated
upgrade:
	mise run upgrade --sync
check:
	mise run default
test:
	mise run test
ci:
	mise run ci
