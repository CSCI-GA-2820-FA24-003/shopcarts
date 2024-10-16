
# NYU DevOps Project - Shopcarts

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This project implements the shopcarts service, which allows customers to manage a collection of products they want to purchase. The service includes a REST API that provides CRUD operations for managing shopcarts and the items within them.

In Sprint 1, we are following Test Driven Development (TDD) practices to create and test the models and service routes for the shopcarts resource.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.gitattributes      - File to fix Windows CRLF issues
.flaskenv           - Environment variables to configure Flask
Dockerfile          - Docker configuration file
pyproject.toml      - Poetry list of Python libraries required

service/                        - service python package
├── __init__.py                 - package initializer
├── config.py                   - configuration parameters
├── models.py                   - model for shopcarts and items
├── routes.py                   - module with service routes
├── common                      - common code package
│   ├── cli_commands.py         - Flask command to recreate all tables
│   ├── error_handlers.py       - HTTP error handling code
│   ├── log_handlers.py         - logging setup code
│   └── status.py               - HTTP status constants

tests/                          - test cases package
├── __init__.py                 - package initializer
├── factories.py                - Factory for testing with fake objects
├── test_models.py              - test suite for business models
└── test_routes.py              - test suite for service routes
```

## API Endpoints

The shopcarts service currently provides the following API endpoints:

| Method | URL                                          | Operation                                   |
|--------|----------------------------------------------|---------------------------------------------|
| GET    | `/`                                          | Return some JSON about the service          |
| GET    | `/shopcarts`                                 | List all shopcarts                          |
| POST   | `/shopcarts`                                 | Create a new shopcart                       |
| GET    | `/shopcarts/{id}`                            | Read a shopcart                             |
| PUT    | `/shopcarts/{id}`                            | Update a shopcart                           |
| DELETE | `/shopcarts/{id}`                            | Delete a shopcart                           |
| GET    | `/shopcarts/{id}/items`                      | List all items in a shopcart                |
| POST   | `/shopcarts/{id}/items`                      | Create a new item in a shopcart             |
| GET    | `/shopcarts/{id}/items/{item_id}`            | Read an item from a shopcart                |
| PUT    | `/shopcarts/{id}/items/{item_id}`            | Update an item in a shopcart                |
| DELETE | `/shopcarts/{id}/items/{item_id}`            | Delete an item from a shopcart              |

### Root Route
The root route `/` returns information about the service, including its name and version in JSON format.

## Running the Tests

To run the tests for this project, use the following command:

```bash
make test
```

This command will run the test suite using `pytest` to ensure that all the tests pass.

## Running the Service Locally

To run the shopcarts service locally, use the following command:

```bash
honcho start
```

The service will start and be accessible at `http://localhost:8080`.

## Coding Standards

Make sure that your code conforms to the PEP8 Python standard by using `pylint`. The `make lint` command can be used to run pylint and check for compliance.

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
