###########
# Aliases #
###########

build: build.pyz


###################
# Common commands #
###################


# Clean cached files
#
# Usage:
#	make clean

clean:
	find src -name "__pycache__" -delete
	find src -name "*.pyc" -delete



##################
# Build commands #
##################

# Build applitoolsify.pyz.
#
# Usage:
#	make build.pyz [download=(yes|no)]
build.pyz: clean
	$(if $(call eq,$(download),no),,python downloader.py)
	mkdir -p dist
	python -m zipapp --compress src --main "applitoolsify.cli:run" --output dist/applitoolsify.pyz
