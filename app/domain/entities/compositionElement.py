from pydantic import BaseModel


class SubCompositionElement(BaseModel):
    name: str


class CompositionELement(BaseModel):
    name: str
    sub_elements: list[SubCompositionElement] | None = None
