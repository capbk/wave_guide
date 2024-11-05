run:
	gunicorn --bind 0.0.0.0:8080 --timeout 120 wsgi:app

install:
	pip3 install -r requirements.txt

run_non_wsgi:
	source app_env; python app.py;

test:
	python3 -m pytest tests/ -v

test-coverage:
	python3 -m pytest tests/ -v --cov=recommendation_engine --cov-report=term-missing