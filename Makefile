.PHONY: setup install serve

setup:
	virtualenv --python=python3.6 venv

install:
	pip install -r requirements.txt

serve:
	FLASK_APP=run_app.py FLASK_DEBUG=1 flask run
