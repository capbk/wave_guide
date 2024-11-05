run:
	gunicorn --bind 0.0.0.0:8080 --timeout 120 wsgi:app

install:
	pip3 install -r requirements.txt
	npm init -y

test-backend:
	python3 -m pytest tests/ -v

test-frontend:
	npm test

test-backendcoverage:
	python3 -m pytest tests/ -v --cov=recommendation_engine --cov-report=term-missing