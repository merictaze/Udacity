from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatalogItem
from CatalogDAO import CatalogDAO
from CatalogHelper import *
import json

dao = CatalogDAO()

# Create dummy user
id = dao.createUser({'username': 'Meric',
                     'email': 'info@merictaze.com',
                     'picture': ''})

# Insert the test data from json file to database
with open('database_populate.json') as f:
    data = json.load(f)
    for category in data['catalog']:
        newCategory = dao.createCategory(category['name'])
        for item in category['item']:
            dao.createItem(name=item['name'],
                           description=item['description'],
                           image=sendGETRequest(item['url'])[1],
                           user_id=id,
                           category=newCategory)
