import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

TABLE = {
  'category': 'category',
  'catalog_item': 'catalog_item',
  'user': 'user'
}


class User(Base):
    __tablename__ = TABLE['user']

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)


class Category(Base):
    __tablename__ = TABLE['category']

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    def serialize(self, session):
        return {
            'name': self.name,
            'id': self.id,
            'items': [item.serialize for item in session.query(
                        CatalogItem).filter_by(category_id=self.id)]
        }


class CatalogItem(Base):
    __tablename__ = TABLE['catalog_item']

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(400), nullable=False)
    time_create = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey('%s.id' % TABLE['user']))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('%s.id' % TABLE['category']))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }

    def __repr__(self):
        return ("<CatalogItem(name=%s, user_id=%s, category_id=%s)"
                % (self.name, self.user_id, self.category_id))

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
