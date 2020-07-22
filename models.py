from config import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from collections import OrderedDict
from marshmallow import pre_load
from sqlalchemy import func

#DATABASE SCHEMA--------------------------------


class Polls(db.Model):
    __tablename__ = "polltable"
    pollid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pollname = db.Column(db.String(32), default=None)
    questions = db.relationship(
        "Questions",
        backref="polltable",
        cascade="all, delete, delete-orphan",
        single_parent=True,
    )


class Questions(db.Model):
    __tablename__ = "questiontable"
    questionid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pollid = db.Column(db.Integer, db.ForeignKey("polltable.pollid"))
    questiontype = db.Column(db.String, nullable=False)
    minselection = db.Column(db.Integer, nullable=False)
    maxselection = db.Column(db.Integer, nullable=False)
    questiontext = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=True)
    option3 = db.Column(db.String, nullable=True)
    option4 = db.Column(db.String, nullable=True)
    option5 = db.Column(db.String, nullable=True)
#-------------------------------------------------------------------
# SCHEMA TO LOAD POLLS

class LPollSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Polls
        load_instance = True
        ordered = True
        include_relationships = True
        sqla_session = db.session

    questions = fields.Nested('LQuestionSchema', many=True, default=[])


class LQuestionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Questions
        fields = 'questiontype', 'minselection', 'maxselection', 'questiontext', 'option1', \
                 'option2', 'option3', 'option4', 'option5',
        load_instance = True
        ordered = True
        include_fk = True
        sqla_session = db.session

    settings = fields.Dict()
    description = fields.Str()
    options = fields.List(fields.Dict())

    @pre_load()
    def make_question(self, obj, **kwargs):
        print(obj)

        questionform = {
            'questiontype': obj['settings']['questionType'],
            'minselection': obj['settings']['minSelection'],
            'maxselection': obj['settings']['maxSelection'],
            'questiontext': obj['description'],

            'option1': obj['options'][0]['description']}
        try:
            o2 = {'option2': obj['options'][1]['description']}
        except:
            o2 = {'option2': None}
        try:
            o3 = {'option3': obj['options'][2]['description']}
        except:
            o3 = {'option3': None}
        try:
            o4 = {'option4': obj['options'][3]['description']}
        except:
            o4 = {'option4': None}
        try:
            o5 = {'option5': obj['options'][4]['description']}
        except:
            o5 = {'option5': None}

        questionform.update(o2)
        questionform.update(o3)
        questionform.update(o4)
        questionform.update(o5)


        return questionform
# -------------------------------------------------------------------------------------------------------------------

class Responses(db.Model):

    __tablename__ = "responsetable"
    responseid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer)
    pollRequestId = db.Column(db.Integer, db.ForeignKey("polltable.pollid"))
    answers= db.relationship(
        "Answers",
        backref="responsetable",
        cascade="all, delete"
    )


class Answers(db.Model):
    __tablename__ = "answertable"
    answerid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    responseid = db.Column(db.Integer, db.ForeignKey("responsetable.responseid"))
    questionumber = db.Column(db.Integer)
    response1 = db.Column(db.Integer, nullable=True)
    response2 = db.Column(db.Integer, nullable=True)
    response3 = db.Column(db.Integer, nullable=True)
    response4 = db.Column(db.Integer, nullable=True)
    response5 = db.Column(db.Integer, nullable=True)

#-------------------------------------------------------------------------------------
#SCHEMA FOR LOADING OF RESPONSE

class LResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Responses
        load_instance = True
        include_fk = True
        ordered = True
        include_relationships = True
        sqla_session = db.session

    userId = fields.Int()
    pollRequestId = fields.Int()
    answers = fields.Nested("LAnswerSchema", many=True)


class LAnswerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Answers
        fields = 'questionumber','response1','response2' ,'response3' ,'response4','response5'
        load_instance = True
        include_relationships = True
        include_fk = True

        sqla_session = db.session

    questionId = fields.Int()
    optionId = fields.List(fields.Int())

    @pre_load()
    def make_answer(self, obj, **kwargs):
        print(obj)
        r = {}
        for j in range(1, 6):
            try:

                r.update({'response' + str(j): j}) if j in obj['optionId'] else r.update({'response' + str(j): None})
            except:
                r.update({'response' + str(j): None})

        questionumber = {'questionumber': obj['questionId']}
        r.update(questionumber)

        return r

#--------------------------------------------------------------------------------------------------------------
#SCHEMA TO DUMP POLLS


class PollSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = Polls
        load_instance = True
        ordered = True
        include_relationships = True
        sqla_session = db.session

    id = fields.Function(lambda obj: obj.pollid)
    questions =  fields.Nested("QuestionSchema",exclude=("pollid",),default=[],many=True)


class QuestionSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = Questions
        load_instance = True
        ordered = True
        exclude = 'questiontext', 'questionid', 'questiontype','maxselection', 'minselection', 'option1', 'option2', \
                  'option3', 'option4', 'option5'
        include_fk = True
        sqla_session = db.session

    id = fields.Method("getnumber")
    description = fields.Function(lambda obj: obj.questiontext)
    options = fields.Method("getoptions")
    settings = fields.Method("getsettings")

    def getnumber(self, obj):

        minid = db.session.query(func.min(Questions.questionid)).filter(Questions.pollid == obj.pollid).scalar()

        questionumber = (obj.questionid - minid)+1

        return questionumber

    def getsettings(self, obj):
        return OrderedDict({'id': obj.pollid,'questionType': obj.questiontype,
                            'minSelection': obj.minselection, 'maxSelection': obj.maxselection,"questionId": obj.questionid })

    def getoptions(self, obj):
        return [{'id':1,'description': obj.option1},{'id':2, 'description': obj.option2},{'id':3, 'description':obj.option3},
                {'id': 4, 'description': obj.option4},{'id':5, 'description':obj.option5}]

#---------------------------------------------------------------------------------------------------------------------
#RESPONSE 201 FOR POLL SUBMIT
class SPollSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = Polls
        load_instance = True
        ordered = True
        include_relationships = True
        sqla_session = db.session

    id = fields.Function(lambda obj: obj.pollid)
    questions =  fields.Nested("SQuestionSchema",exclude=("pollid",),default=[],many=True)


class SQuestionSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = Questions
        load_instance = True
        exclude = 'questiontext', 'questionid', 'questiontype','maxselection', 'minselection', 'option1', 'option2', \
                  'option3', 'option4', 'option5'
        ordered = True
        include_fk = True
        sqla_session = db.session

    id = fields.Method("getnumber")
    description = fields.Function(lambda obj: obj.questiontext)
    pollRequestId = fields.Function(lambda obj: obj.pollid)
    options = fields.Method("getoptions")
    settings = fields.Method("getsettings")

    def getnumber(self, obj):

        minid = db.session.query(func.min(Questions.questionid)).filter(Questions.pollid == obj.pollid).scalar()

        questionumber = (obj.questionid - minid)+1

        return questionumber

    def getsettings(self, obj):
        minid = db.session.query(func.min(Questions.questionid)).filter(Questions.pollid == obj.pollid).scalar()

        questionumber = (obj.questionid - minid) + 1
        return OrderedDict({'id': obj.pollid,'questionType': obj.questiontype,
                            'minSelection': obj.minselection, 'maxSelection': obj.maxselection,"questionId": questionumber })

    def getoptions(self, obj):
        minid = db.session.query(func.min(Questions.questionid)).filter(Questions.pollid == obj.pollid).scalar()

        questionumber = (obj.questionid - minid) + 1

        return [{'id':1,'description': obj.option1, "questionId": questionumber },
                {'id':2, 'description': obj.option2, "questionId": questionumber},
                {'id':3, 'description':obj.option3, "questionId": questionumber},
                {'id': 4, 'description': obj.option4, "questionId": questionumber},
                {'id':5, 'description':obj.option5, "questionId": questionumber}]


# ------------------------------------------------------------------------------------------------------------------------

#SCHEMA TO DUMP FOR RESPONSE 201

class ResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Responses
        load_instance = True
        exclude = 'responseid',
        include_fk = True
        ordered = True
        include_relationships = True
        sqla_session = db.session

    Id = fields.Function(lambda obj: obj.responseid)
    userId = fields.Int()
    pollRequestId = fields.Int()
    answers = fields.Nested("AnswerSchema", many=True)
    pollRequest = fields.Method("getpoll")

    def getpoll(self, obj):
        pollid = obj.pollRequestId
        pschema = SPollSchema(only=('id','questions'),many=True)
        pollquery = db.session.query(Polls).filter(Polls.pollid == pollid).join(Questions)
        poll = pschema.dump(pollquery)

        return  poll



class AnswerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Answers
        fields = 'questionumber','response1','response2' ,'response3' ,'response4','response5'
        load_instance = True
        ordered = True
        include_relationships = True
        include_fk = True
        sqla_session = db.session

    Id = fields.Function(lambda obj: obj.answerid)
    questionId = fields.Int()
    optionId = fields.List(fields.Int())
    pollResponseId = fields.Method("getpollresponseid")

    def getpollresponseid(self, obj):
        responseid = obj.responseid
        pollid = db.session.query(Responses.pollRequestId).filter(Responses.responseid == responseid ).scalar()
        responsequery = db.session.query(Responses.responseid).filter(Responses.pollResponseId == pollid ).all()
        responseslist = [r for r, in responsequery]
        pollresponseid = responseslist.index(responseid)+1


        return {'pollResponseId': pollresponseid }
#----------------------------------------