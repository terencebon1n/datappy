import importlib

import backend.infrastructure.config as config_module

_PROD_ENV = {
    "ENV": "prod",
    "PROD_POSTGRES__HOST": "prod-db",
    "PROD_POSTGRES__PORT": "5432",
    "PROD_POSTGRES__DATABASE": "prod",
    "PROD_POSTGRES__USERNAME": "prod-user",
    "PROD_POSTGRES__PASSWORD": "prod-pass",
    "PROD_POSTGRES__CONFIG__POOL_SIZE": "10",
    "PROD_POSTGRES__CONFIG__MAX_OVERFLOW": "5",
    "PROD_POSTGRES__CONFIG__POOL_RECYCLE": "300",
    "PROD_POSTGRES__CONFIG__POOL_TIMEOUT": "30",
    "PROD_KAFKA__BROKERS": "prod-broker:9092",
    "PROD_REDIS__HOST": "prod-redis",
    "PROD_REDIS__PORT": "6379",
    "PROD_ADMIN__ALLOWED_EMAIL": "admin@prod.local",
    "PROD_ADMIN__SESSION_SECRET_KEY": "prod-secret",
    "PROD_ADMIN__DOCKER_IMAGE": "datappy:prod",
    "PROD_ADMIN__DOCKER_NETWORK": "prod-net",
    "PROD_ADMIN__GOOGLE__CLIENT_ID": "prod-client",
    "PROD_ADMIN__GOOGLE__CLIENT_SECRET": "prod-client-secret",
    "PROD_ADMIN__GOOGLE__REDIRECT_URI": "http://prod/callback",
}


def test_default_settings_are_staging():
    assert config_module.settings.env == "stg"
    assert config_module.postgres_url.drivername == "postgresql+psycopg"


def test_default_feeds_cover_all_cities():
    assert len(config_module.settings.feeds) == 4


def test_kafka_config_to_spark_options():
    kc = config_module.KafkaConfig(
        bootstrap_servers="b:9092",
        starting_offsets="latest",
        max_offsets_per_trigger=1000,
    )
    assert kc.to_spark_options() == {
        "kafka.bootstrap.servers": "b:9092",
        "startingOffsets": "latest",
        "maxOffsetsPerTrigger": "1000",
    }


def test_app_config_from_yaml(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        "kafka:\n"
        "  bootstrap_servers: 'broker:29092'\n"
        "  starting_offsets: 'latest'\n"
        "  max_offsets_per_trigger: 500\n"
        "  security:\n"
        "    protocol: 'SSL'\n"
    )
    cfg = config_module.AppConfig.from_yaml(str(path))
    assert cfg.kafka.bootstrap_servers == "broker:29092"
    assert cfg.kafka.max_offsets_per_trigger == 500


def test_production_settings_branch(monkeypatch, tmp_path):
    """Reload the module under ENV=prod to execute the production branch."""
    # Run from a directory without a real ``.env`` so production settings come
    # purely from the injected PROD_* environment.
    monkeypatch.chdir(tmp_path)
    for key, value in _PROD_ENV.items():
        monkeypatch.setenv(key, value)
    try:
        reloaded = importlib.reload(config_module)
        assert reloaded.settings.env == "prod"
        assert reloaded.settings.postgres.host == "prod-db"
        assert reloaded.postgres_url.host == "prod-db"
    finally:
        monkeypatch.setenv("ENV", "stg")
        importlib.reload(config_module)

    # restored to staging for the rest of the session
    assert config_module.settings.env == "stg"
