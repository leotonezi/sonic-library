from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")

class ApiResponse(GenericModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = "Success"
    status: str = "ok"