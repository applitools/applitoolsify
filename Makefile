###########
# Aliases #
###########

build: build.pyz



##################
# Build commands #
##################

# Build applitoolsify.pyz.
#
# Usage:
#	make build.pyz [download=(yes|no)]
build.pyz:
	find src -name "__pycache__" -delete
	find src -name "*.pyc" -delete
	$(if $(call eq,$(download),no),,python downloader.py)
	mkdir -p dist
	python -m zipapp --compress src --main "applitoolsify.cli:run" --output dist/applitoolsify.pyz
