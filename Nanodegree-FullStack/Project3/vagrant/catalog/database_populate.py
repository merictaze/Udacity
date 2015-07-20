from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatalogItem
import datetime

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
newUser = User(name="Meric", email="mer.ich@hotmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(newUser)
session.commit()

newCategory = Category(name="Soccer")
session.add(newCategory)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()


newCategory = Category(name="Basketball")
session.add(newCategory)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Jersey", description="desc2", category=newCategory, user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Soccer Cleats", description="desc1", category=newCategory, user=newUser)
session.add(newItem)
session.commit()