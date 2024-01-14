from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
from sqlalchemy.orm import Session
from apps import models, security, schemas  # Explicitly import the modules
from apps.db import engine, get_db
from apps.routes import router
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ID = "chatengine_project_id"
PRIVATE_KEY = "chatengine_private_key"

class User(BaseModel):
    username: str
    secret: str
    email: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    
@router.post('/register/', response_model=schemas.UserInDBBase)
async def signup(user_in: schemas.UserIn, db: Session = Depends(get_db)):
    # First, attempt to register the user locally, as in CODE 1
    db_user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(**user_in.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # After local registration is successful, register the user with ChatEngine
    chatengine_response = requests.post(
        'https://api.chatengine.io/users/', 
        data={
            "username": user_in.username,
            "secret": user_in.secret,
            "email": user_in.email,
            "first_name": user_in.first_name,
            "last_name": user_in.last_name,
        },
        headers={"Private-Key": PRIVATE_KEY}
    )
    # Check the response from ChatEngine and handle any errors
    if not chatengine_response.ok:
        # Handle the error accordingly (e.g., rollback the local user creation, log the error, etc.)
        raise HTTPException(status_code=chatengine_response.status_code, detail="Failed to register user with ChatEngine")

    # Return the user data along with the ChatEngine registration response
    return {
        "local_user": db_user,
        "chatengine_response": chatengine_response.json()
    }
    
    
@router.post('/login/')
async def login(user: schemas.UserIn, db: Session = Depends(get_db)):
    # Local authentication
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # After successful local authentication, verify the user with ChatEngine
    chatengine_response = requests.get(
        'https://api.chatengine.io/users/me/', 
        headers={ 
            "Project-ID": PROJECT_ID,
            "User-Name": user.username,
            "User-Secret": user.password  # Assuming the secret is the user's password
        }
    )

    # Check the response from ChatEngine and handle any errors
    if not chatengine_response.ok:
        # Handle the error accordingly (you might want to return a specific message or log the error)
        raise HTTPException(status_code=chatengine_response.status_code, detail="ChatEngine authentication failed")

    # Return the user data along with the ChatEngine authentication response
    return {
        "local_user": {"username": db_user.username, "message": "User authenticated locally"},
        "chatengine_response": chatengine_response.json()
    }


models.Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="127.0.0.1", port=3009)

