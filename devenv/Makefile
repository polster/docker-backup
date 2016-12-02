.PHONY: run

docker-run:
	docker-compose up -d
	docker ps -a

docker-destroy-env:
	docker stop repo repodata
	docker rm repo repodata

install-dependencies:
	pip install docker-py
