import sqlalchemy
from sqlalchemy.orm import relationship

from database import Base


class Card(Base):
    __tablename__ = 'cards'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=255))
    age = sqlalchemy.Column(sqlalchemy.String(length=255))
    skill = sqlalchemy.Column(sqlalchemy.String(length=255))
    market_value = sqlalchemy.Column(sqlalchemy.Integer, default=100)
    market_price = sqlalchemy.Column(sqlalchemy.Integer, default=100)
    on_market = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = relationship("User", back_populates="cards")
