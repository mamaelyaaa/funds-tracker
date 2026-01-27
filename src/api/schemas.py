from pydantic import BaseModel


class BaseExceptionSchema(BaseModel):
    message: str
    suggestion: str
