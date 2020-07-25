install:
	python setup.py install
	pip install .
	@$(MAKE) -s clean

clean:
	rm -rf .pytest_cache build dist .coverage *.egg-info

test:
	pytest --flake8 --cov=now_and_later

test_pep257:
	pep257 now_and_later/ tests/ -s

test_all:
	@$(MAKE) -s test
	@$(MAKE) -s test_pep257
