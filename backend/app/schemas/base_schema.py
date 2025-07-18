from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = "Success"
    status: str = "ok"

class PaginationResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: dict
    message: Optional[str] = "Success"
    status: str = "ok"