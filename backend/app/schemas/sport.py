from pydantic import BaseModel


class SportResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
