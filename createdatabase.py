from config import db
from models import Polls, Questions, Responses, Answers, LPollSchema

# Data to initialize database with
#poll contains 3 questions
#Pollname is optional

poll = {"pollname": "firstpoll","questions": [{"settings": {
                "questionType": "single",
                "minSelection": 1,
                "maxSelection": 1},"description": "Choose your favourite car?",
            "options": [{ "description": "BMW"  },{"description": "Audi"},{"description": "Benz"},{"description": "Ferrari"},
                {"description": "Ferrari"}]},{"settings": {
                "questionType": "2opt",
                "minSelection": 1,
                "maxSelection": 2},"description": "Choose your favourite letter?",
            "options": [{ "description": "A"  },{"description": "B"},{"description": "C"},{"description": "D"},
                {"description": "E"}]},{"settings": {
                "questionType": "three",
                "minSelection": 1,
                "maxSelection": 3},"description": "Choose your favourite sport?",
            "options": [{ "description": "cricket"  },{"description": "football"},{"description": "kabaddi"}]}]}




# Create the database
db.create_all()

lschema = LPollSchema(many=True)
new_poll = lschema.load([poll], session=db.session)
# Add the poll to the database
db.session.add(new_poll[0])
db.session.commit()
