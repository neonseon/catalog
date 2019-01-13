import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
           'email'        : self.email,
           'picture'      : self.picture
       }


class ApiCategory(Base):
    __tablename__ = 'api_category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    slug = Column(String(250), nullable=False, unique=True)


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Api(Base):
    __tablename__ = 'api'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    url = Column(String(80), nullable=False)
    slug = Column(String(250), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('api_category.id'))
    api_category = relationship(ApiCategory, backref='offerings')
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///api.db')


Base.metadata.create_all(engine)