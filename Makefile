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

# Install required packages for build.
#
# Usage:
#	make download.sdk

install.build:
	pip install dohq-artifactory

# Download Applitools SKDs.
#
# Usage:
#	make download.sdk
download.sdk:
	python downloader.py


# Build applitoolsify.pyz.
#
# Usage:
#	make build.pyz
build.pyz: clean install.build download.sdk
	mkdir -p dist
	python -m zipapp --compress src --main "applitoolsify.cli:run" --output dist/applitoolsify.pyz
