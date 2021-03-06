
black:
	black .

clean:
	-rm -r build/*
	find src/ -name '*.pyc' -exec sudo rm -f {} +
	find src/ -name '*.pyo' -exec sudo rm -f {} +
	find src/ -name '*~' -exec rm -f {} +
	find src/ -name '__pycache__' -exec sudo rm -fr {} +
	find src/ -name '*.htm' -exec rm -f {} +
	find src/ -name '*.html' -exec rm -f {} +
	find src/ -name '*.so' -exec rm -f {} +
	find src/ -name 'octave-workspace' -exec rm -f {} +
	-rm -r dist/*
	-rm -r src/*.egg-info

release:
	make clean
	python setup.py sdist bdist_wheel
	python setup.py sdist
	gpg --detach-sign -a dist/abgleich*.whl
	gpg --detach-sign -a dist/abgleich*.tar.gz

install:
	pip install -vU pip setuptools
	pip install -v -e .[all]

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done
