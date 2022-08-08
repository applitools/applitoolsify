build-pyz:
	find src -name "__pycache__" -delete
	find src -name "*.pyc" -delete
	python -m zipapp src -o applitoolsify.pyz -m "applitoolsify.cli:run"
