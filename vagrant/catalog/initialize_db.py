from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CatItem, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Add testing data
user1 = User(auth_id="1", name="admin")
session.add(user1)
session.commit()

category1 = Category(name="Pets", description="Stuff for pets.", user_id=1)

session.add(category1)
session.commit()

catItem1 = CatItem(name="bone", description="Bone for dogs.",
                   category=category1, user_id=1)

session.add(catItem1)
session.commit()

print "added catalog items!"
