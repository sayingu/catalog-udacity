# This Python file uses the following encoding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, CategoryItem

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

# initital user it's me!
user = User(name=u"\xec\xa7\x84\xec\x83\x81\xed\x98\xb8",
            email="sayingu@gmail.com", picture="")
session.add(user)
session.commit()

# Street category and items
category = Category(name="Street")

session.add(category)
session.commit()

categoryItem = CategoryItem(
    title="BMW-M3 Coupe 1999",
    description="Max 6 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Mazda-RX-7 FD",
    description="Max 6 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Porsche-911 (993) Carrera",
    description="Max 6 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Toyota-Supra",
    description="Max 6 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

# Classic Sports category and items
category = Category(name="Classic Sports")

session.add(category)
session.commit()

categoryItem = CategoryItem(
    title="Ford-Fiesta ST",
    description="Max 5 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Subaru-BRZ",
    description="Max 5 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Toyota-86",
    description="Max 5 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

categoryItem = CategoryItem(
    title="Volkswagen-Golf GTI",
    description="Max 5 stars",
    category=category, user=user)

session.add(categoryItem)
session.commit()

# Muscle category
category = Category(name="Muscle")

session.add(category)
session.commit()

# Sports category
category = Category(name="Sports")

session.add(category)
session.commit()

# Super category
category = Category(name="Super")

session.add(category)
session.commit()

# Hyper category
category = Category(name="Hyper")

session.add(category)
session.commit()

print "added category items!"
