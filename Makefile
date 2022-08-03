build:
	find src -name "__pycache__"|xargs rm -rf
	find src -name "*.pyc"|xargs rm -rf
	python -m zipapp src -o applitoolsify.pyz -m "src.cli:run"
