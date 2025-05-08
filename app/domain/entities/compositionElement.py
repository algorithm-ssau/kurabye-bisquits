from pydantic import BaseModel, Field


class SubCompositionElement(BaseModel):
    name: str


class CompositionELement(BaseModel):
    element_id: int
    name: str
    is_allergen: bool = Field(default=False)
    sub_elements: list[SubCompositionElement] | None = None
