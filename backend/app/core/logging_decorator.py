import logging
import asyncio
from fastapi import HTTPException
from functools import wraps
import inspect
from typing import Optional

logger = logging.getLogger("sonic")

def log_exceptions(endpoint_name: Optional[str] = None, log_response: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = endpoint_name or func.__name__
            logger.info(f"{name} - Called")
            try:
                result = func(*args, **kwargs)
                
                # Check if the function is async and await it if necessary
                if inspect.iscoroutine(result):
                    result = asyncio.run(result)
                
                # Log response details only if explicitly requested
                if log_response:
                    if isinstance(result, dict):
                        # Extract key info for logging
                        status = result.get('status', 'unknown')
                        message = result.get('message', '')
                        data_type = type(result.get('data', '')).__name__
                        data_length = len(result.get('data', [])) if isinstance(result.get('data', ''), (list, dict)) else 'N/A'
                        
                        logger.debug(f"{name} - Success: status={status}, message='{message}', data_type={data_type}, data_length={data_length}")
                    else:
                        logger.debug(f"{name} - Success: {type(result).__name__}")
                else:
                    logger.info(f"{name} - Success")
                
                return result
            except HTTPException as e:
                logger.warning(f"{name} - HTTPException: {e.detail}")
                raise
            except Exception as e:
                logger.exception(f"{name} - Unhandled Exception")
                raise HTTPException(status_code=500, detail=f"{str(e)}")
        return wrapper
    return decorator