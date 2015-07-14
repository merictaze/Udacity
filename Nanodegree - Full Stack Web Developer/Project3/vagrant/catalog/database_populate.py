from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

newCategory = Category(name="Soccer")
session.add(newCategory)
session.commit();

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory)
session.add(newItem)
session.commit()


newCategory = Category(name="Basketball")
session.add(newCategory)
session.commit();
