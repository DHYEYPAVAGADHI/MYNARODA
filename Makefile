# ============================================================
# GREEN NARODA • CLEAN NARODA — Makefile
# Common developer commands. Run `make help` to see all.
# ============================================================

.PHONY: help install dev shell migrate makemigrations test lint format clean

# Default Python / Django settings
PYTHON = python
MANAGE = $(PYTHON) manage.py
SETTINGS = config.settings.development

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ────────────────────────────────────────────────────────────────────

install:  ## Install development dependencies
	pip install -r requirements/development.txt

setup: install  ## Full first-time setup (install, env copy, migrate, superuser)
	@if [ ! -f .env ]; then cp .env.example .env; echo "⚠  .env created — fill in your values!"; fi
	$(MANAGE) migrate --settings=$(SETTINGS)
	$(MANAGE) createsuperuser --settings=$(SETTINGS)

# ─── Development ──────────────────────────────────────────────────────────────

dev:  ## Run the development server
	$(MANAGE) runserver 0.0.0.0:8000 --settings=$(SETTINGS)

shell:  ## Open Django shell_plus
	$(MANAGE) shell_plus --settings=$(SETTINGS)

worker:  ## Start Celery worker
	celery -A config worker --loglevel=info

beat:  ## Start Celery beat scheduler
	celery -A config beat --loglevel=info

# ─── Database ─────────────────────────────────────────────────────────────────

migrate:  ## Apply all pending migrations
	$(MANAGE) migrate --settings=$(SETTINGS)

makemigrations:  ## Create new migration files
	$(MANAGE) makemigrations --settings=$(SETTINGS)

showmigrations:  ## Show migration status
	$(MANAGE) showmigrations --settings=$(SETTINGS)

resetdb:  ## ⚠ DROP and recreate the development database (irreversible!)
	dropdb mynaroda_dev --if-exists
	createdb mynaroda_dev
	$(MANAGE) migrate --settings=$(SETTINGS)

# ─── Static Files ─────────────────────────────────────────────────────────────

collectstatic:  ## Collect static files
	$(MANAGE) collectstatic --noinput --settings=$(SETTINGS)

# ─── Translations ─────────────────────────────────────────────────────────────

messages:  ## Extract translatable strings
	$(MANAGE) makemessages -l gu -l hi --settings=$(SETTINGS)

compilemessages:  ## Compile translation files
	$(MANAGE) compilemessages --settings=$(SETTINGS)

# ─── Testing ──────────────────────────────────────────────────────────────────

test:  ## Run all tests with coverage
	pytest apps/ --cov=apps/ --cov-report=html --cov-report=term-missing -v

test-fast:  ## Run tests without coverage (faster)
	pytest apps/ -v

# ─── Code Quality ─────────────────────────────────────────────────────────────

lint:  ## Run ruff linter
	ruff check .

format:  ## Auto-format code with ruff and isort
	ruff format .
	isort .

typecheck:  ## Run mypy type checker
	mypy apps/ core/ services/ selectors/

check: lint typecheck  ## Run all code quality checks

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean:  ## Remove Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
