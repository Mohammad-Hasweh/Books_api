from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from src.books.schemas import Book, BookUpdateModel, bookCreateModel
from src.books.service import BookService
from src.db.main import get_session
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import TokenBearer,AccessTokenBearer,RoleChecker
from src.errors import BookNotFound



book_router = APIRouter()
book_service = BookService()
acess_token_bearer = AccessTokenBearer()
role_checker=Depends(RoleChecker(["admin","user"]))


# CTRL + SHIFT + L for replacing all the same words in the file
@book_router.get("/", response_model=List[Book],dependencies=[role_checker])
async def get_user_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer),
):
    user_uid = token_details.get("user")["user_uid"]
    books = await book_service.get_user_books(user_uid,session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book,dependencies=[role_checker])
async def create_book(
    book_data: bookCreateModel, 
    session: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer)
) -> dict:
    
    user_uid = token_details.get("user")["user_uid"]
    print("this is a test")

    new_book = await book_service.create_book(book_data,user_uid, session)

    return new_book

@book_router.get("/{book_uid}", response_model=Book,dependencies=[role_checker])
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session),token_details=Depends(acess_token_bearer)) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise BookNotFound()


# !!! note BookUpdate  works as the validator for the data we shall use to update the book record.
@book_router.patch("/{book_uid}", response_model=Book,dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    seesion: AsyncSession = Depends(get_session),
    token_details=Depends(acess_token_bearer)
) -> dict:

    updated_book = await book_service.update_book(book_uid, book_update_data, seesion)

    if updated_book is None:
        raise BookNotFound()

    else:
        return updated_book


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[role_checker])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session),
                      token_details=Depends(acess_token_bearer)):
    deleted_book = await book_service.delete_book(book_uid, session)
    if deleted_book is None:
        raise BookNotFound()
    else:
        return {}
