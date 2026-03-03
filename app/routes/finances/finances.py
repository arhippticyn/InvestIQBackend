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


@router.get('/category/incomes', response_model=List[FinanceResponse])
async def get_incomes_by_category(category_id: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Income).where(Income.category_id == category_id, Income.user_id == user.id))).scalars().all()


@router.delete('/incomes/clear')
async def clear_incomes(db: AsyncSession = Depends(get_db)):
    incomes = (await db.execute(select(Income))).scalars().all()

    for income in incomes:
       await db.delete(income)
    await db.commit()

    return {'message': 'Incomes creared success'}

@router.delete('/incomes/{id}', response_model=FinanceResponse)
async def delete_income_by_id(id: int, user = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    income = (await db.execute(select(Income).where((Income.user_id == user.id) & (Income.id == id)))).scalars().first()

    if income:
        await db.delete(income)
        await db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Income not found')

    return income


# expenses

@router.post('/expense', response_model=FinanceResponse)
async def create_expense(expense_data: FinanceCreate, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    expense = expense_data.model_dump()

    new_expense = Expense(**expense, user_id=user.id)
     
    db.add(new_expense)

    await db.commit()
    await db.refresh(new_expense)

    return new_expense


@router.get('/expense', response_model=List[FinanceResponse])
async def get_expenses(user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Expense).where(Expense.user_id == user.id))).scalars().all()


@router.get('/expense/{id}', response_model=FinanceResponse)
async def get_expense_by_id(id: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Expense).where(Expense.id == id, Expense.user_id == user.id))).scalars().first()


@router.patch('/expense/{id}', response_model=FinanceResponse)
async def set_amount_expense(id: int, new_amount: int,user: User = Depends(get_currunt_user) ,db: AsyncSession = Depends(get_db)):
    expense = (await db.execute(select(Expense).where(Expense.id == id, Expense.user_id == user.id))).scalars().first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')

    if new_amount:
        expense.amount = new_amount
        await db.commit()
        await db.refresh(expense)

    return expense


@router.get('/category/expense', response_model=List[FinanceResponse])
async def get_expenses_by_category(category_id: int, user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Expense).where(Expense.category_id == category_id, Expense.user_id == user.id))).scalars().all()

@router.delete('/expense/clear')
async def clear_expense(db: AsyncSession = Depends(get_db)):
    expenses = (await db.execute(select(Expense))).scalars().all()

    for expense in expenses:
        await db.delete(expense)
    
    await db.commit()

    return {'message': 'Expenses creared success'}


@router.delete('/expense/{id}')
async def delete_expense_by_id(id: int,user: User = Depends(get_currunt_user), db: AsyncSession = Depends(get_db)):
    expense = (await db.execute(select(Expense).where(Expense.id == id, Expense.user_id == user.id))).scalars().first()

    if not expense:
       raise HTTPException(status_code=404, detail="Expense not found")

    await db.delete(expense)
    await db.commit()

    return id


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


