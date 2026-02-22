from fastapi import APIRouter, status, Depends, HTTPException
from app.models.finances import Category, Income, Expense
from app.models.user import User
from app.services.auth import get_currunt_user
from app.schemas.finances import FinanceCreate, FinanceResponse, CategoryCreate, CategoryResponse
from sqlalchemy import select
from app.db.sessions import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()

# incomes

@router.post('/incomes', response_model=FinanceResponse)
async def create_income(income_data: FinanceCreate, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    income = income_data.model_dump()

    new_income = Income(**income, user=user)
     
    db.add(new_income)

    await db.commit()
    await db.refresh(new_income)

    return new_income


@router.get('/incomes', response_model=List[FinanceResponse])
async def get_incomes(user = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    incomes = (await db.execute(select(Income).where(Income.user_id == user.id))).scalars().all()

    return incomes


@router.get('/incomes/{id}', response_model=FinanceResponse)
async def get_income_by_id(id: int, user = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    income = (await db.execute(select(Income).where((Income.user_id == user.id) & (Income.id == id)))).scalars().first()

    if income:
        return income
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Income not found"')



@router.delete('/incomes/{id}', response_model=FinanceResponse)
async def delete_income_by_id(id: int, user = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    income = (await db.execute(select(Income).where((Income.user_id == user.id) & (Income.id == id)))).scalars().first()

    if income:
        await db.delete(income)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Income not found"')

    return income


# expenses

@router.post('/expense', response_model=FinanceResponse)
async def create_expense(expense_data: FinanceCreate, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    expense = expense_data.model_dump()

    new_expense = Expense(**expense, user=user)
     
    db.add(new_expense)

    await db.commit()
    await db.refresh(new_expense)

    return new_expense

# categories

@router.post('/category', response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    category = category_data.model_dump()

    new_category = Category(**category)
     
    db.add(new_category)

    await db.commit()
    await db.refresh(new_category)

    return new_category


@router.get('/category', response_model=List[CategoryResponse])
async def get_categories(user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(Category))).scalars().all()

    return categories


@router.get('/category/{id}', response_model=CategoryResponse)
async def get_category_by_id(id: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    category = (await db.execute(select(Category).where(Category.id == id))).scalars().first()

    if category:
        return category
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found"')


@router.delete('/category/{id}', response_model=CategoryResponse)
async def delete_category_by_id(id: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    category = (await db.execute(select(Category).where(Category.id == id))).scalars().first()

    if category:
        await db.delete(category)
        await db.commit()

        return category
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found"')



