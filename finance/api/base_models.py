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

class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None
    tags: Optional[List[str]] = None

    @field_validator("type")
    def validate_type(cls, v):
        if v and v not in ["income", "expense"]:
            raise ValueError("Type must be income or expense")
        return v

    @field_validator("category")
    def validate_category(cls, v):
        if v and (not v or v != v.lower()):
            raise ValueError("Category must be lowercase and non-empty")
        return v

class Category(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v):
        if not v:
            raise ValueError("Category name must not be empty")
        return v.lower()

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["income", "expense", "both"]:
            raise ValueError("Type must be income, expense or both")
        return v

class CategoryPatch(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None

    @field_validator("type")
    def validate_type(cls, v):
        if v not in ["income", "expense", "both"]:
            raise ValueError("Type must be income, expense or both")
        return v
