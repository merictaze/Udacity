from flask import make_response
from flask import session as login_session
from functools import wraps
import httplib2
import json


def login_required(f):
    """Checks whether user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in login_session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def createJSONResponse(msg, errorCode):
    """Helper function to create JSON response"""
    response = make_response(json.dumps(msg), errorCode)
    response.headers['Content-Type'] = 'application/json'
    return response


def sendGETRequest(url):
    """Sends a GET request to the given url"""
    h = httplib2.Http()
    return h.request(url, 'GET')


def sendDELETERequest(url):
    """Sends a DELETE request to the given url"""
    h = httplib2.Http()
    return h.request(url, 'DELETE')


def createdByUser(item):
    """Check whether item is created by the user

    Args:
        item: item whose user_id field will be checked with
              the logged in user
    """
    return ('user_id' in login_session and
            login_session['user_id'] == item.user_id)
