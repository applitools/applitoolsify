build-pyz:
	find src -name "__pycache__" -delete
	find src -name "*.pyc" -delete
	python downloader.py
	mkdir -p dist
	python -m zipapp --compress src --main "applitoolsify.cli:run" --output dist/applitoolsify.pyz
