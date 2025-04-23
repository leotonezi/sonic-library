from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = "Success"
    status: str = "ok"