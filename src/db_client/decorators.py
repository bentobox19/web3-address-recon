import functools

def locked(lock_attribute_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            lock = getattr(self, lock_attribute_name)
            async with lock:
                return await func(self, *args, **kwargs)
        return wrapper
    return decorator
