# Bookly API

A comprehensive RESTful API for managing books, authors, and publications, built with **FastAPI** and **SQLModel**.

## Overview

This project demonstrates how to build a robust and scalable backend API for a digital library system using modern Python tools and best practices. It covers everything from basic CRUD operations to advanced topics such as authentication, role-based access control, async database handling, and background tasks.

## Features

- FastAPI server setup and routing  
- Handling path, query, and optional query parameters  
- Request body validation and header management  
- Organized API routes with routers  
- Database integration with SQLModel (based on SQLAlchemy and Pydantic)  
- Async support and database schema migrations using Alembic  
- Clean separation of CRUD logic via service classes  
- Dependency Injection for modular and testable code  
- User authentication with JWT tokens and password hashing  
- Role-Based Access Control (RBAC)  
- Complex model and schema relationships  
- Custom error handling and API exception management  
- Middleware for logging, CORS, trusted hosts, and more  
- Email support and user account verification with FastAPI-Mail  
- Password reset functionality  
- Background task processing using Celery and Redis, with task monitoring

## Technologies Used

- Python 3.9+  
- FastAPI  
- SQLModel  
- Alembic  
- JWT (PyJWT)  
- Passlib (for password hashing)  
- Redis & Celery (for background tasks)  
- FastAPI-Mail  
- PostgreSQL 


