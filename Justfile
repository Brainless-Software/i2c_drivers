#!/usr/bin/env -S just --justfile

set default-list := true

mkdocs:
    mkdocs build & sleep 1 & mkdocs gh-deploy

test-cov-all:
    pytest --cov=i2c_drivers --rootdir=src --cov-report=html ; xdg-open htmlcov/index.html

test-cov-mcp2221:
    pytest --cov=i2c_drivers --rootdir=src --cov-report=html tests/test.py::test_mcp2221 ; xdg-open htmlcov/index.html

test-cov-i2cdriver:
    pytest --cov=i2c_drivers --rootdir=src --cov-report=html tests/test.py::test_i2cdriver ; xdg-open htmlcov/index.html

test-cov-ft232h:
    pytest --cov=i2c_drivers --rootdir=src --cov-report=html tests/test.py::test_ft232h ; xdg-open htmlcov/index.html