from pydantic import BaseModel, Field, field_validator
from typing import List,Optional
from datetime import date

class Transaction(BaseModel):
    title: str = Field(...,min_length=3,max_length=100)
    description: Optional[str] = Field(None,max_length=100)
    amount: float = Field(...,gt=0)
    type : str
    category: str
    date: Optional[str]
    tags : Optional[List[str]] = None

    @field_validator('title')
    def validate_title(cls, value):
        return value.strip()
    @field_validator('type')
    def validate_type(cls, value):
        if value not in ['income','expense']:
            raise ValueError('Type must be either income or expense')
        return value
    @field_validator('category')
    def validate_category(cls, value):
        if not value:
            raise ValueError('Category cannot be empty')
        if value!=value.lower():
            raise ValueError('Category must be lowercase')
        return value
    @field_validator('tags')
    def validate_tags(cls, value):
        if len(value)>10:
            raise ValueError('Tags cannot be longer than 10 characters')
        for tag in value:
            if len(tag)>30:
                raise ValueError('Tags cannot be longer than 30 characters')
        return value