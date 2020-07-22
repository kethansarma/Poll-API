"""
This is the poll module and supports all the REST actions for the
poll data
"""

from flask import make_response, abort
from config import db
from models import Polls, PollSchema, Questions,\
LPollSchema,Responses, ResponseSchema, LResponseSchema
from sqlalchemy import func
from flask import  url_for


def read_all():
    """
    This function responds to a request for /api/poll
    with list of 2 recent poll

    :return:        json string of list of polls
    """
    # Create the list of recent polls from our data
    poll = Polls.query.order_by(Polls.pollid.desc()).limit(2).all()

    # Serialize the data for the response
    poll_schema = PollSchema(only=('id','questions'),many=True)
    data = poll_schema.dump(poll)

    return data


def getrequest(pollid):
    """
    This function responds to a request for /api/poll/{pollid}
    with one matching poll from polls

    :param pollid:   Id of poll to find
    :return:            poll matching id
    """
    # Build the initial query
    poll = Polls.query.filter(Polls.pollid == int(pollid)).join(Questions).all()


    # Did we find a poll?
    if poll:

        # Serialize the data for the response
        poll_schema = PollSchema(only=('id','questions'),many=True)
        data = poll_schema.dump(poll)
        return data

    # Otherwise, nope, didn't find that poll
    else:
        if(404):
            abort(404, f"Poll not found for Id: {pollid}")
        if (400):
            abort(400, 'Bad Request')
        if (500):
            abort(500)


def create(poll):
    """
    This function creates a new poll

    :param poll:  poll to create
    :return:        201 on success
    """

    # Create a poll instance using the schema
    lschema = LPollSchema(many=True)

    new_poll = lschema.load([poll], session=db.session)

    # Add the poll to the database
    if new_poll:
        db.session.add(new_poll[0])
        db.session.commit()

    # Serialize and return the newly created poll through request api in the response
        pollid = db.session.query(func.max(Polls.pollid)).scalar()


        return url_for("/api.poll_getrequest", pollid =pollid )
    else:
        if (400):
            abort(400)
        if (500):
            abort(500)

def getresponse(responseid):
    """
    This function responds to a request for /api/poll/getresponse/{responseid}
    with one matching response from responses

    :param responseid:   Id of response to find
    :return:            responses matching id
    """
    # Build the initial query


    exists = db.session.query(Responses.responseid ).filter(Responses.responseid == responseid).scalar()is not None

    if(exists):
        response = db.session.query(Responses).filter(Responses.responseid == responseid).all()
        responseschema = ResponseSchema(many=True)
        data = responseschema.dump(response)

        return data


    else:
        if(404):
            abort(404,f"Response not found for Id: {responseid}")
        if(500):
           abort(500)


def submit(response):
    """
    This function updates an existing poll response

    :param response:   response of the poll to post
    :return:            posted response accessed with getresponse api
    """
    # Get the person requested from the db into session

    pollid = response.get('pollRequestId')


    pollidexist = Polls.query.filter(Polls.pollid == pollid)

    # Did we find an existing poll?
    if pollidexist is not None:

        # turn the passed in poll into a db object
        lschema = LResponseSchema()

        new_response = lschema.load([response],many=True, session=db.session)
        # merge the new object into the old and commit it to the db
        db.session.add(new_response[0])
        db.session.commit()

        responseid = db.session.query(func.max(Responses.responseid)).scalar()

        return url_for('/api.poll_getresponse',responseid=responseid)



    else:
        if (400):
            abort(400,"Bad request")
        if (500):
            abort(500)


def delete(pollid):
    """
    This function deletes a poll from the polls

    :param pollid:   Id of the poll to delete
    :return:         204 on successful delete, 404 if not found
    """
    # Get the poll requested
    poll = Polls.query.filter(Polls.pollid == pollid).one_or_none()


    if poll is not None:
        db.session.delete(poll)
        db.session.commit()

        return make_response(f"No content for Poll id {pollid}", 204)

    # Otherwise, nope, didn't find that polls
    else:
        if(404):
            abort(404, f"Poll not found for Id: {pollid}")
        if(500):
            abort(500)
