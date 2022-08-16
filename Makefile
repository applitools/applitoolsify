build-pyz:
	find src -name "__pycache__" -delete
	find src -name "*.pyc" -delete
	#python downloader.py
	python -m zipapp --compress src --main "applitoolsify.cli:run" --output applitoolsify.pyz
