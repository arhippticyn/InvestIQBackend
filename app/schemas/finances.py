from pydantic import BaseModel
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


class BaseCategory(BaseModel):
    name: str


class CategoryCreate(BaseCategory):
    pass
    

class CategoryResponse(BaseCategory):
    id: int
