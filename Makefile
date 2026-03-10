# TelsonBase Makefile
# Common developer commands. Run `make help` to see all targets.

.PHONY: help test test-unit test-security test-integration lint clean build run stop logs shell migrate

# Default target
help:
	@echo "TelsonBase — Available Make Targets"
	@echo ""
	@echo "  Development"
	@echo "    make install       Install all dev dependencies"
	@echo "    make run           Start all Docker services"
	@echo "    make stop          Stop all Docker services"
	@echo "    make build         Build Docker images without starting"
	@echo "    make logs          Follow logs for mcp_server"
	@echo "    make shell         Open a shell inside the mcp_server container"
	@echo "    make migrate       Run Alembic database migrations"
	@echo ""
	@echo "  Testing"
	@echo "    make test          Run full test suite (unit + integration, no stress)"
	@echo "    make test-unit     Run unit tests only (no Docker services required)"
	@echo "    make test-security Run 96-test security battery"
	@echo "    make test-stress   Run MQTT stress tests"
	@echo ""
	@echo "  Code Quality"
	@echo "    make lint          Run isort check + bandit security scan"
	@echo "    make lint-fix      Auto-fix import sorting"
	@echo ""
	@echo "  Cleanup"
	@echo "    make clean         Remove __pycache__, .pytest_cache, coverage files"

# ──────────────────────────────────────────────────────────────
# Development
# ──────────────────────────────────────────────────────────────

install:
	pip install -r requirements-dev.txt

run:
	docker compose up -d

stop:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f mcp_server

shell:
	docker compose exec mcp_server /bin/bash

migrate:
	docker compose exec mcp_server python -m alembic upgrade head

# ──────────────────────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────────────────────

test:
	docker compose exec mcp_server python -m pytest tests/ -v --tb=short \
		--ignore=tests/test_mqtt_stress.py

test-unit:
	python -m pytest tests/ -v --tb=short -x \
		--ignore=tests/test_e2e_integration.py \
		--ignore=tests/test_mqtt_stress.py \
		-k "not integration"

test-security:
	docker compose exec mcp_server python -m pytest tests/test_security_battery.py -v --tb=short

test-stress:
	docker compose exec mcp_server python -m pytest tests/test_mqtt_stress.py -v --tb=short

# ──────────────────────────────────────────────────────────────
# Code Quality
# ──────────────────────────────────────────────────────────────

lint:
	isort --check-only --diff core/ api/ agents/
	bandit -r core/ api/ agents/ -ll

lint-fix:
	isort core/ api/ agents/

# ──────────────────────────────────────────────────────────────
# Cleanup
# ──────────────────────────────────────────────────────────────

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f .coverage coverage.xml
	rm -rf htmlcov/
