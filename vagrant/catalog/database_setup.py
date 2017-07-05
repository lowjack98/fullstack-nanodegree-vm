import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    items = relationship("CatItem", cascade='all,delete-orphan')

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }


class CatItem(Base):
    __tablename__ = 'cat_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    auth_id = Column(Integer, nullable=False)
    name = Column(String(80), nullable=False)
    email = Column(String(80))

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'auth_id': self.auth_id,
            'name': self.name,
            'email': self.email
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
