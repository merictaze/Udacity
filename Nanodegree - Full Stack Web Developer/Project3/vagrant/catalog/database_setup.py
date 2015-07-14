import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

TABLE = {
  'category': 'category',
  'catalog_item': 'catalog_item'
}

class Category(Base):
    __tablename__ = TABLE['category']
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class CatalogItem(Base):
    __tablename__ = TABLE['catalog_item']
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(400), nullable=False)
    category_id = Column(Integer, ForeignKey('%s.id' % TABLE['category']))
    category = relationship(Category)

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
