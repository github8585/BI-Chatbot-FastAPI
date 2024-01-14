from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy.orm import Session
from apps import auth, models, schemas, security
from apps.db import get_db
from apps.models import User
from apps.prompt import *
from apps.llmcontext import retrieve_from_db
from dotenv import load_dotenv, find_dotenv
from apps.llmcontext import retrieve_from_db

load_dotenv(find_dotenv())

router = APIRouter()

@router.post("/register/", response_model=schemas.UserInDBBase)
async def register(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_secret = security.secret(user_in.secret)
    db_user = models.User(
        **user_in.dict(exclude={"secret"}), secret=hashed_secret
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth.get_user(db, username=form_data.username)
    if not user or not security.pwd_context.verify(
        form_data.password, user.secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/login/')
async def login(user: schemas.UserIn, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not security.secret(user.secret):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "User authenticated", "user": db_user.username}
 
@router.post("/conversation/")
async def read_conversation(
    query: str,
    current_user: schemas.UserInDBBase = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).get(current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    context = generate(query)

    llm = OpenAI(
        temperature=0.7,
        openai_api_key="openai_api_key"
    )
 
    response = generate(query)

    return {"response": response}