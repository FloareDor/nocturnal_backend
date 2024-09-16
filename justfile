# Define default shell for Unix-like systems
set shell := ["bash", "-cu"]

set windows-powershell := true

default:
  just --list

run *args:
  poetry run uvicorn src.main:app --host 0.0.0.0 --reload {{args}}

mm *args:
  poetry run alembic revision --autogenerate -m "{{args}}"

migrate:
  poetry run alembic upgrade head

downgrade *args:
  poetry run alembic downgrade {{args}}

ruff *args:
  poetry run ruff check {{args}} src

lint:
  poetry run ruff format src
  just ruff --fix

# Docker commands
up:
  docker-compose up -d

kill *args:
  docker-compose kill {{args}}

build:
  docker-compose build

ps:
  docker-compose ps
