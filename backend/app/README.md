## Project Structure

```
src/
├── core/
│   ├── config.py
│   ├── security.py         # Logto JWKS fetching and base verify_jwt
│   ├── permissions.py      # Global Enum registry of all scopes
│   ├── database.py         # MongoDB client and Beanie init function
│   ├── logging.py
│   ├── exceptions.py
│   ├── middleware.py
│   └── health.py
├── api/
│   ├── router.py           # Master router aggregating feature routers
│   └── system.py           # /health and /metrics
├── features/
│   ├── users/
│   │   ├── __init__.py     # EXPORTS: feature_models = [User]
│   │   ├── router.py
│   │   ├── service.py      # Accepts UserRepository via dependency injection
│   │   ├── repository.py
│   │   ├── models.py       # Beanie Documents (Strictly internal to feature)
│   │   ├── schemas.py      # Pydantic DTOs (The public contract)
│   │   └── dependencies.py # get_current_user lives HERE, returns a Schema
│   └── organizations/
│       ├── __init__.py     # EXPORTS: feature_models = [Organization, Member]
│       ├── router.py       # Imports get_current_user from users.dependencies
│       └── ...
└── main.py                 # Imports feature_models to pass to init_beanie()
tests/
├── conftest.py
├── unit/
└── integration/
```
