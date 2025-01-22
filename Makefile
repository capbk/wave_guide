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

install-qdrant:
	# stuck on docker 4.25.0 with mac OS big sur https://desktop.docker.com/mac/main/amd64/126437/Docker.dmg
	# docker login; enter credentials
	docker pull qdrant/qdrant:v1.7.4

run-qdrant:
	docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant:v1.7.4
