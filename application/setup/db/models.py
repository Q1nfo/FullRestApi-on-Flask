from sqlalchemy import Column, DateTime, func, Integer

from application.setup.db import db


# =====================BASE MODELS IN ORM TO INHERIT =============================================

class Base(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime, nullable=False, default=func.now())
    updated = Column(DateTime, default=func.now(), onupdate=func.now())
