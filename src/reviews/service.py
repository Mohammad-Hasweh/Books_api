import logging

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select,desc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review

from .schemas import ReviewCreateModel

from src.errors import (BookNotFound,UserNotFound,)

book_service=BookService()
user_service=UserService()



class ReviewService:
    async def add_review_to_book(self,user_email:str,
    book_uid:str,
    review_data:ReviewCreateModel,
    session:AsyncSession):
        try:
            book=await book_service.get_book(book_uid=book_uid,session=session)
            user=await user_service.get_user_by_email(user_email,session)

            review_data_dict=review_data.model_dump()
            new_review=Review(**review_data_dict)
            
            if not book:
                raise BookNotFound()
            if not user:
                raise UserNotFound()
            new_review.user=user
            new_review.book=book

            await session.commit()

            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops... something went wrong"
            )

    async def get_review(self,review_uid,session:AsyncSession):
        statment=select(Review).where(Review.uid==review_uid)

        result= await session.exec(statment)

        return result.first()

    async def get_all_reviews(self,session:AsyncSession):
        statment=select(Review).order_by(desc(Review.created_at))

        result=await session.exec(statment)

        return result.all() 

    async def delete_review_to_from_book(
            self,review_uid:str,user_email:str,session:AsyncSession
    ):
        user=await user_service.get_user_by_email(user_email,session)
        review=await self.get_review(review_uid,session)

        if not review or (review.user not in user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Cannot delete this review.")
        
        session.delete(review)
        
        await session.commit()