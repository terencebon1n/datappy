"""Global test configuration.

Deterministic environment is injected at import time (before pytest collects
any test module) so that ``backend.infrastructure.config`` — which instantiates
its ``Settings`` singleton at import — never depends on the real ``.env`` file.
Values set here take precedence over the ``.env`` file in pydantic-settings.
"""

import os

_TEST_ENV = {
    "ENV": "stg",
    "STG_POSTGRES__HOST": "test-db",
    "STG_POSTGRES__PORT": "5432",
    "STG_POSTGRES__DATABASE": "test",
    "STG_POSTGRES__USERNAME": "test-user",
    "STG_POSTGRES__PASSWORD": "test-pass",
    "STG_POSTGRES__CONFIG__POOL_SIZE": "10",
    "STG_POSTGRES__CONFIG__MAX_OVERFLOW": "5",
    "STG_POSTGRES__CONFIG__POOL_RECYCLE": "300",
    "STG_POSTGRES__CONFIG__POOL_TIMEOUT": "30",
    "STG_KAFKA__BROKERS": "test-broker:9092",
    "STG_REDIS__HOST": "test-redis",
    "STG_REDIS__PORT": "6379",
    "STG_ADMIN__ALLOWED_EMAIL": "admin@test.local",
    "STG_ADMIN__SESSION_SECRET_KEY": "test-secret-key",
    "STG_ADMIN__DOCKER_IMAGE": "datappy:test",
    "STG_ADMIN__DOCKER_NETWORK": "test-net",
    "STG_ADMIN__FRONTEND_URL": "http://localhost:8001",
    "STG_ADMIN__GOOGLE__CLIENT_ID": "test-client-id",
    "STG_ADMIN__GOOGLE__CLIENT_SECRET": "test-client-secret",
    "STG_ADMIN__GOOGLE__REDIRECT_URI": "http://localhost:8000/admin/callback",
}

for _key, _value in _TEST_ENV.items():
    os.environ[_key] = _value
