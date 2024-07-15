from pydantic import BaseModel


class LinkSchema(BaseModel):
    id: int
    url: str
    description: str | None
    tag_id: int


class TagSchema(BaseModel):
    id: int
    name: str
