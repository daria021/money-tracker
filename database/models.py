from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    username = Column(String, primary_key=True, unique=True)
    rent = Column(Float, default=0.0)
    clothes = Column(Float, default=0.0)
    transport = Column(Float, default=0.0)
    food = Column(Float, default=0.0)
    house = Column(Float, default=0.0)
    pets = Column(Float, default=0.0)
    spinner = Column(Float, default=0.0)
    other = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"User @{self.username}"
