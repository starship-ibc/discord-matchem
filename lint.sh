#!/usr/bin/env bash

poetry run isort matchem
poetry run black matchem
poetry run flake8 matchem
