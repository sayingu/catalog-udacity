from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    """User tabel (id, name, email, picture)"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):

    """Categories table (id, name)"""
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id": self.id,
            "name": self.name
        }


class CategoryItem(Base):

    """Items table (id, title, description, category_id)"""
    __tablename__ = "category_item"

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id
        }

engine = create_engine("postgresql://catalog:catalog@localhost/catalog")

Base.metadata.create_all(engine)
