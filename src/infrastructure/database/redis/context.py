from redis.client import Pipeline, Redis


class RedisPipelineContext:
    def __init__(self, host="redis", port=6379):
        self.host: str = host
        self.port: int = port

    def __enter__(self):
        self.client: Redis = Redis(
            host=self.host, port=self.port, decode_responses=True
        )
        self.pipe: Pipeline = self.client.pipeline()
        return self

    def add_to_pipeline(self, key: str, field: str, value: str, ttl: int = 300):
        self.pipe.hset(key, field, value)
        self.pipe.expire(key, ttl)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.pipe.execute()
        self.client.close()
