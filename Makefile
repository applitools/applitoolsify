build:
	python setup.py sdist

publish-test:
	twine upload --verbose -r test dist/*

publish-prod:
	twine upload --verbose -r pypi dist/*

clean:
	rm -rf dist applitoolsify.egg-info

build-publish:
	$(MAKE) build
	$(MAKE) publish-test
	$(MAKE) clean