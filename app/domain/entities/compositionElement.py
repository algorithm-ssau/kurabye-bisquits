from pydantic import BaseModel, Field


class SubCompositionElement(BaseModel):
    name: str


class CompositionELement(BaseModel):
    element_id: int | None = None
    name: str | None = Field(default=None)
    is_allergen: bool | None = Field(default=False)
    sub_elements: list[SubCompositionElement] | None = None
