DOCKER_COMPOSE := docker compose
SERVICE_NAME := app

EXEC_PYTHON := $(DOCKER_COMPOSE) exec $(SERVICE_NAME) python
EXEC_ALEMBIC := $(DOCKER_COMPOSE) exec $(SERVICE_NAME) alembic
EXEC_PYTEST := $(DOCKER_COMPOSE) exec $(SERVICE_NAME) pytest

.PHONY: help up down build logs shell migrate rollback migration test prune

# Отображение справки
help:
	@echo "Доступные команды:"
	@echo "  make up          - Запустить контейнеры в фоновом режиме"
	@echo "  make down        - Остановить и удалить контейнеры"
	@echo "  make build       - Пересобрать образы"
	@echo "  make rebuild     - Пересобрать образы и запустить контейнер"
	@echo "  make logs        - Показать логи контейнеров"
	@echo "  make shell       - Войти в оболочку контейнера (bash)"
	@echo "  make migrate     - Применить все миграции Alembic"
	@echo "  make rollback    - Откатить последнюю миграцию"
	@echo "  make migration   - Создать новую миграцию (требуется аргумент message)"
	@echo "  make test        - Запустить тесты pytest"
	@echo "  make prune       - Очищает ненужные контейнеры"

# Запуск контейнеров
up:
	$(DOCKER_COMPOSE) up -d

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Пересборка образов (полезно после изменения Dockerfile или requirements.txt)
build:
	$(DOCKER_COMPOSE) build --no-cache

# Пересборка и запуск контейнеров
rebuild:
	$(DOCKER_COMPOSE) up -d --build

# Просмотр логов
logs:
	$(DOCKER_COMPOSE) logs $(SERVICE_NAME) -f

# Вход в контейнер
shell:
	$(DOCKER_COMPOSE) exec $(SERVICE_NAME) bash

# Применить миграции
migrate:
	$(EXEC_ALEMBIC) upgrade head

# Откатить одну миграцию назад
rollback:
	$(EXEC_ALEMBIC) downgrade -1

# Создать новую миграцию
# Использование: make migration message="add users table"
migration:
	$(EXEC_ALEMBIC) revision --autogenerate -m "$(message)"

# Запуск тестов
# Использование: make tests params="-m unit"
test:
	$(DOCKER_COMPOSE) exec -e APP__ENV=TEST $(SERVICE_NAME) pytest $(params)

# Очистка неиспользуемых образов, контейнеров и сетей
prune:
	docker system prune -f
