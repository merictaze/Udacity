from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatalogItem


class CatalogDAO:
    """Data Access Object for the application tables"""

    def __init__(self):
        engine = create_engine('sqlite:///catalog.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def close(self):
        if self.session is not None:
            self.session.close()

    def createCategory(self, name):
        """Inserts a new category into the database"""
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        return category

    def getCategories(self):
        """Returns the all categories"""
        return self.session.query(Category).all()

    def getCategory(self, category_id):
        """Returns the category with the given category_id"""
        return self.session.query(Category).filter_by(id=category_id).one()

    def getLatestItems(self):
        """Returns items recently added"""
        return self.session.query(CatalogItem).join(
                              CatalogItem.category).order_by(
                              CatalogItem.time_create.desc()).limit(10)

    def createItem(self, **kwargs):
        """Inserts a new item into the database"""
        item = CatalogItem(name=kwargs['name'],
                           description=kwargs['description'],
                           image=kwargs['image'],
                           user_id=kwargs['user_id'],
                           category=kwargs['category'])
        self.session.add(item)
        self.session.commit()
        return item

    def updateItem(self, item, data):
        """Updates the given item with the new values"""
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'category_id' in data:
            item.category_id = data['category_id']
        if 'image' in data:
            item.image = data['image']
        self.session.add(item)
        self.session.commit()

    def deleteItem(self, item_id):
        """Deletes the item whose id is item_id"""
        item = self.getItem(item_id)
        self.session.delete(item)
        self.session.commit()

    def getItem(self, item_id):
        """Returns the item with the given item_id"""
        return self.session.query(CatalogItem).filter_by(id=item_id).one()

    def getItemsByCategory(self, category_id):
        """Returns all items in the given category"""
        return self.session.query(CatalogItem).filter_by(
                                  category_id=category_id)

    def createUser(self, data):
        """Creates a new user in the database

        Returns:
            id of the newly created user
        """
        user = User(name=data['username'],
                    email=data['email'],
                    picture=data['picture'])
        self.session.add(user)
        self.session.commit()
        return self.getUserID(data['email'])

    def getUser(self, user_id):
        """Fetches user from the databse by id
        Args:
            user_id: id of the user
        Returns:
            User object corresponding the given id
        """
        return self.session.query(User).filter_by(id=user_id).one()

    def getUserID(self, email):
        """Returns user id by the given email"""
        try:
            user = self.session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None
