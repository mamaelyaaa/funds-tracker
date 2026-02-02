DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
APP_FILE = docker-compose.yml

.PHONY: all
all:
	${DC} -f ${APP_FILE} up --build -d

.PHONY: stop
stop:
	${DC} -f ${APP_FILE} stop

.PHONY: test
test:
	pytest -s -v
