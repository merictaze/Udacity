from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatalogItem
import datetime

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
newUser = User(name="Meric", email="info@merictaze.com",
             picture='')
session.add(newUser)
session.commit()

newCategory = Category(name="Books & Audible")
session.add(newCategory)
session.commit()

newItem = CatalogItem(name="Introduction to Algorithms",
                      description="Some books on algorithms are rigorous but incomplete; others cover masses of material but lack rigor. Introduction to Algorithms uniquely combines rigor and comprehensiveness. The book covers a broad range of algorithms in depth, yet makes their design and analysis accessible to all levels of readers. Each chapter is relatively self-contained and can be used as a unit of study.",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Elements of Programming Interviews",
                      description="The sampler should give you a very good idea of the quality and style of our book. In particular, be sure you are comfortable with the level and with our C++ coding style.",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Head First Design Patterns",
                      description="At any given moment, someone struggles with the same software design problems you have. And, chances are, someone else has already solved your problem. This edition of Head First Design Patterns-now updated for Java 8-shows you the tried-and-true, road-tested patterns used by developers to create functional, elegant, reusable, and flexible software.",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()


newCategory = Category(name="Movies, Music & Games")
session.add(newCategory)
session.commit()

newItem = CatalogItem(name="Squier by Fender Mini Strat Electric Guitar",
                      description="Laminated hardwood body with gloss polyurethane finish. Maple neck with 9.5 in radius rosewood fingerboard with 20 medium frets. It has 3 single-coil pickups. It has hard-tail 6-saddle bridge. Master volume and master tone controls with 5 position selector switch",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Fender Mini Deluxe Amp",
                      description="Affordable mini amplifier for your guitar. Great for practicing in bedrooms, hotel rooms and more. Single 8 ohm, two-inch speaker with 1 watt of power. Headphone jack for private playback. Powered by a single 9V battery",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()

newItem = CatalogItem(name="Fender Performance Guitar Cable 10' Black",
                      description="Extra thick 8mm diameter black PVC jacket to reduce handling noise. Extreme pliability to alleviate kinking. Commercial-grade connectors with 90% copper coverage shield. Package contains 1 Cable",
                      category=newCategory,
                      user=newUser)
session.add(newItem)
session.commit()


newCategory = Category(name="Electronics & Computers")
session.add(newCategory)
session.commit()

newCategory = Category(name="Home, Garden & Tools")
session.add(newCategory)
session.commit()

newCategory = Category(name="Beauty, Health & Grocery")
session.add(newCategory)
session.commit()

newCategory = Category(name="Toys, Kids & Baby")
session.add(newCategory)
session.commit()

newCategory = Category(name="Clothing, Shoes & Jewelry")
session.add(newCategory)
session.commit()

newCategory = Category(name="Sports & Outdoors")
session.add(newCategory)
session.commit()

newCategory = Category(name="Automotive & Industrial")
session.add(newCategory)
session.commit()
