from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.engine.url import make_url

dbUrl = 'sqlite:///catalog.db'
url = make_url(dbUrl)
engine = create_engine(dbUrl)
os.remove(url.database)
