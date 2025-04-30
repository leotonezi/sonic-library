import logging
from fastapi import HTTPException
from functools import wraps

logger = logging.getLogger("sonic")

def log_exceptions(endpoint_name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = endpoint_name or func.__name__
            logger.info(f"{name} - Called")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{name} - Success: {result}")
                return result
            except HTTPException as e:
                logger.warning(f"{name} - HTTPException: {e.detail}")
                raise
            except Exception as e:
                logger.exception(f"{name} - Unhandled Exception")
                raise HTTPException(status_code=500, detail=f"Error in {name}")
        return wrapper
    return decorator