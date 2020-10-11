from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import chatter


# orm implementation of sqlalchemy
class DataBase:
    engine = create_engine('sqlite:///db.db', echo=True)  # creating a local sqlite db with debugging enabled
    chatter.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def exists(self, chat):
        return str(self.session.query(chatter.Chatter).filter_by(twitch_id=chat.twitch_id).first()) != 'None'

    def add(self, chat):
        if not self.exists(self, chat):
            # make sure to add a user doesn't exist in the database before you try to add him
            self.session.add(chat)
            self.session.commit()

    def add_points(self, chat, amount):
        self.session.query(chatter.Chatter).filter_by(twitch_id=chat.twitch_id).first().points += amount
        self.session.commit()

    def add_points_bulk(self, chatters_id, amount):
        # need to send chatter instead of chatter id but it requires a bit of rework
        for chat in chatters_id:
            self.session.query(chatter.Chatter).filter_by(twitch_id=chat).first().points += amount
        self.session.commit()

    def add_guesses(self, chat):
        self.session.query(chatter.Chatter).filter_by(twitch_id=chat.twitch_id).first().guesses += 1
        self.session.commit()

    def get_points(self, chat):
        return self.session.query(chatter.Chatter).filter_by(twitch_id=chat.twitch_id).first().points

    def get_guesses(self, chat):
        return self.session.query(chatter.Chatter).filter_by(twitch_id=chat.twitch_id).first().guesses
