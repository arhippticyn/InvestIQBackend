from pydantic import BaseModel, ConfigDict
from datetime import datetime

class BaseFinance(BaseModel):
    description: str
    amount: int
    date: datetime
    category_id: int


class FinanceCreate(BaseFinance):
    pass


class FinanceResponse(BaseFinance):
    id: int 
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class BaseCategory(BaseModel):
    name: str


class CategoryCreate(BaseCategory):
    pass
    

class CategoryResponse(BaseCategory):
    id: int

    model_config = ConfigDict(from_attributes=True)

