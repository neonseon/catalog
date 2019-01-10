from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import ApiCategory, Base, Api, User

engine = create_engine('sqlite:///api.db')
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


# Collection for Trivia APIs
api_category1 = ApiCategory(name="Trivia")

session.add(api_category1)
session.commit()

api1 = MenuItem(title="JService.io", description="Serve answers and questions pulled from the televsion show Jeopardy®.",
                     url="http://jservice.io/", api_category=api_category1)

session.add(api1)
session.commit()


api2 = MenuItem(title="Trivia Nerd", description="Open trivia questions with topics from Star Wars® to the TV Show Firefly.",
                     url="https://trivia.propernerd.com/", api_category=api_category1)

session.add(api2)
session.commit()


# Collection for Game APIs
api_category1 = ApiCategory(name="Games")

session.add(api_category1)
session.commit()

api1 = MenuItem(title="Texas Hold 'Em", description="Easily develop a poker texas holdem game, just design the graphic.",
                     url="https://market.mashape.com/vincy/texas-hold-em", api_category=api_category1)

session.add(api1)
session.commit()


api2 = MenuItem(title="Fortnite Tracker", description="An easy way for developers to get information from Fortnite.",
                     url="https://fortnitetracker.com/site-api", api_category=api_category1)

session.add(api2)
session.commit()



# Collection for Lyrics APIs
api_category1 = ApiCategory(name="Lyrics")

session.add(api_category1)
session.commit()

api1 = MenuItem(title="Lyrics.ovh", description="Simple API to retrieve the lyrics of a song.",
                     url="https://lyricsovh.docs.apiary.io/", api_category=api_category1)

session.add(api1)
session.commit()


api2 = MenuItem(title="Musixmatch", description="Over 14 million lyrics in over 50 distinct languages.",
                     url="https://developer.musixmatch.com/", api_category=api_category1)

session.add(api2)
session.commit()


# Collection for Humor APIs
api_category1 = ApiCategory(name="Humor")

session.add(api_category1)
session.commit()

api1 = MenuItem(title="Meme Generator", description="Generate memes with preloaded images plus your copy.",
                     url="http://version1.api.memegenerator.net/", api_category=api_category1)

session.add(api1)
session.commit()


api2 = MenuItem(title="Geek Jokes", description="Fetch a random geeky/programming related joke.",
                     url="https://github.com/sameerkumar18/geek-joke-api", api_category=api_category1)

session.add(api2)
session.commit()


print "added apis!"