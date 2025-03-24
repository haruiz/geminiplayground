.PHONY: deploy publish
publish:
	@echo "Building and publishing package..."
	@export $(shell grep -v '^#' .env | xargs) && \
	uv build && \
	uv publish --token $$PYPI_TOKEN
