COMPOSE_FILE = docker-compose.yml

build:
	docker compose -f $(COMPOSE_FILE) build

up:
	docker compose -f $(COMPOSE_FILE) up -d

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

down:
	docker compose -f $(COMPOSE_FILE) down

clean:
	docker compose -f $(COMPOSE_FILE) down -v

dev:
	$(MAKE) down
	$(MAKE) build
	$(MAKE) up

all_dev:
	$(MAKE) clean
	$(MAKE) build
	$(MAKE) up

concurrency-test:
	docker compose -f $(COMPOSE_FILE) exec api python scripts/concurrency_test.py

prune:
	# Clean the unused Docker data to save disk space
	docker system prune -af