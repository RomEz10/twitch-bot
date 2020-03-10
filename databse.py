from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import chatter


# orm implementation of sqlalchemy
class database:
    engine = create_engine('sqlite:///db.db', echo=True)  # creating a local sqlite db with debugging enabled
    chatter.Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    def add(self, chat):
        exists = str(self.session.query(chatter.Chatter).filter_by(name=chat.id).first()) != 'None'
        if exists:
            self.session.add(chat)
            self.session.commit()


