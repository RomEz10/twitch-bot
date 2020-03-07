from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Chatter(Base):
    __tablename__ = 'chatters'

    id = Column(Integer, primary_key=True)
    twitch_id = Column(Integer)
    name = Column(String)
    points = Column(Integer)
    guesses = Column(Integer)

    def __repr__(self):
        return "<Chatter(twitch_id'%s', name'%s', points='%s', guesses='%s')>" % (
            self.twitch_id, self.name, self.points, self.guesses)
