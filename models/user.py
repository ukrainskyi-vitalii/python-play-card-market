import sqlalchemy
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column("username", sqlalchemy.String(length=255), nullable=False)
    email = sqlalchemy.Column("email", sqlalchemy.String(length=255), unique=True, nullable=False)
    country = sqlalchemy.Column("country", sqlalchemy.String(length=255))
    role = sqlalchemy.Column("role", sqlalchemy.Enum('admin', 'regular', name='user_roles'), default='regular')
    budget = sqlalchemy.Column("budget", sqlalchemy.Integer, default=500)
    cards = relationship("Card", back_populates="user")

    def __init__(self, username, email, country, role, budget):
        self.username = username
        self.email = email
        self.country = country
        self.role = role
        self.budget = budget
