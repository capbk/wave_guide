run:
	gunicorn --bind 0.0.0.0:8080 --timeout 120 wsgi_local:app

install-python:
	pip3 install -r requirements.txt

install-frontend-test-deps:
	npm init -y
	npm install --save-dev jest @testing-library/jest-dom
	npm install --save-dev @testing-library/dom
	npm install --save-dev jest jest-environment-jsdom @babel/preset-env babel-jest

test-backend:
	python3 -m pytest tests/ -v

test-frontend:
	npm test

test-backendcoverage:
	python3 -m pytest tests/ -v --cov=recommendation_engine --cov-report=term-missing