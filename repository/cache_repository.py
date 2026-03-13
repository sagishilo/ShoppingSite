from typing import Optional
from repository.redis import redis_client, config

## Retrieves a value from cache by key if it exists
def get_cache_entity(key: str) -> Optional[str]:
    if redis_client.exists(key):
        return redis_client.get(key)
    else:
        return None

## Creates a new cache entry with TTL if the key doesn't exist
def create_cache_entity(key: str, value: str):
    if not redis_client.exists(key):
        redis_client.setex(key, config.REDIS_TTL, value)

## Updates an existing cache entry and resets its TTL
def update_cache_entity(key: str, value: str):
    if redis_client.exists(key):
        redis_client.setex(key, config.REDIS_TTL, value)

## Deletes a specific entry from cache by key
def remove_cache_entity(key: str):
    if redis_client.exists(key):
        redis_client.delete(key)

## Checks if a specific key exists in the cache
def is_key_exists(key: str) -> bool:
    return redis_client.exists(key)