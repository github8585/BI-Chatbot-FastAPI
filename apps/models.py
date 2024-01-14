from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String
from apps.db import Base
from apps.schemas import UserBase  # corrected import statement
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Mapped

Base = declarative_base()

class User(Base):
    __tablename__ = "userschatbot"

    id: Mapped[int] = Column(Integer, primary_key=True)  # Primary key
    username: Mapped[str] = Column(String, unique=True, index=True)
    secret: Mapped[str] = Column(String)
    email: Mapped[str] = Column(String, unique=True, index=True)
    first_name: Mapped[str] = Column(String)
    last_name: Mapped[str] = Column(String)

