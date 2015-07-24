from flask import Flask, render_template, url_for
from flask import request, redirect, flash, jsonify
from flask import session as login_session
from flask import make_response

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, CatalogItem

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

import requests
import random
import string
import httplib2
import json


app = Flask(__name__)
app.secret_key = 'cvAETf4adFASD4VDS4FB2fas43S5G4gth4T1'

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog/')
def catalog():
    """Shows the list of categories in the system"""
    categories = session.query(Category).all()
    latestItems = session.query(CatalogItem).join(
                    CatalogItem.category).order_by(
                      CatalogItem.time_create.desc()).limit(10)
    return render_template('catalog.html', categories=categories,
                           latestItems=latestItems)


@app.route('/catalog/<int:category_id>/items')
def items(category_id):
    """Shows the list of items in the selected category

    Args:
        category_id: id of the category whose items will be shown in the page
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id)
    return render_template('items.html', category=category, items=items)


@app.route('/catalog/<int:category_id>/item/<int:item_id>')
def item(category_id, item_id):
    """Shows the selected item and its information

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CatalogItem).filter_by(category_id=category.id,
                                                id=item_id).one()
    return render_template('item.html', category=category, item=item,
                           updateAllowed=userAllowed(item.user_id))


@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def itemEdit(category_id, item_id):
    """Lets user edit an item

    Only loggedin user who created the item can edit. Otherwise, user will be
    redirected to home page

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    if not userAllowed(item.user_id):
        return redirect('/')

    if request.method == 'POST':
        if request.form['item_name']:
            item.name = request.form['item_name']
        if request.form['item_description']:
            item.description = request.form['item_description']
        if request.form['item_category']:
            item.category_id = request.form.getlist('item_category')[0]
        session.add(item)
        session.commit()
        flash('Item is updated successfully')
        return redirect(url_for('item', category_id=item.category_id,
                                item_id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template('item_edit.html', categories=categories,
                               item=item)


@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def itemDelete(category_id, item_id):
    """Lets user delete an item

    Only loggedin user who created the item can delete. Otherwise, user will be
    redirected to home page

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    if not userAllowed(item.user_id):
        return redirect('/')

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item "%s" is deleted successfully' % item.name)
        return redirect(url_for('items', category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('item_delete.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def itemAdd():
    """Lets user add an item

    Only loggedin user can add an item
    """
    if not userAllowed():
        return redirect('/')
    if request.method == 'POST':
        if (not request.form['item_name'] or
           not request.form['item_description'] or
           not request.form['item_category']):
            flash('Please fill all the fields in the form')
        else:
            category = session.query(Category).filter_by(
                        id=request.form['item_category']).one()
            newItem = CatalogItem(name=request.form['item_name'],
                                  description=request.form['item_description'],
                                  category=category)
            session.add(newItem)
            session.commit()
            flash('New item is added successfully')

    categories = session.query(Category).all()
    return render_template('item_add.html', categories=categories)


@app.route('/catalog/json')
def catalogJSON():
    """Returns catalog in JSON format"""
    categories = session.query(Category)
    return jsonify(Catalog=[c.serialize(session) for c in categories])


@app.route('/login')
def login():
    """Shows the login form"""
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/connect', methods=['POST'])
def connect():
    """Connects user with a Google/Facebook account"""
    # Validate state token
    if request.json['state'] != login_session['state']:
        return createJSONResponse('Invalid state parameter.', 401)

    if request.json['provider'] == "google":
        data = gconnect(auth_code=request.json['code'])
    else:
        data = fbconnect(access_token=request.json['code'])

    # return error
    if 'success' not in data:
        return data

    # store user info in the session variable
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['access_token'] = data['access_token']
    login_session['provider'] = data['provider']
    login_session['provider_id'] = data['provider_id']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return createJSONResponse('Sucessfully logged in', 200)


def gconnect(auth_code):
    """Helper method to connect with a Google account"""
    try:
        # Exchange the authorization code with a credentials object
        oauth_flow = flow_from_clientsecrets('google_client_secrets.json',
                                             scope='',
                                             redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        return createJSONResponse('Failed to obtain the authorization code.',
                                  401)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)

    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        return createJSONResponse(result.get('error'), 500)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return createJSONResponse("Token's user ID doesn't match given"
                                  "user ID.", 401)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != json.loads(
       open('google_client_secrets.json', 'r').read())['web']['client_id']:
        return createJSONResponse("Token's client ID does not match app's.",
                                  401)

    # check if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return createJSONResponse('Current user is already connected.', 200)

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    data = requests.get(userinfo_url, params=params).json()

    # Store the access token in the session for later use.
    data['access_token'] = access_token
    data['provider'] = 'google'
    data['provider_id'] = gplus_id

    data['success'] = True
    return data


def fbconnect(access_token):
    """Helper method to connect with a Facebook account"""

    clientSecrets = json.loads(open('fb_client_secrets.json', 'r').read())
    app_id = clientSecrets['web']['app_id']
    app_secret = clientSecrets['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token'
           '?grant_type=fb_exchange_token'
           '&client_id=%s&client_secret=%s&fb_exchange_token=%s') % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?fields=id,name,email&%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Get user picture
    url = ('https://graph.facebook.com/v2.2/me/picture?%s'
           '&redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data['picture'] = json.loads(result)["data"]["url"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in
    # our token
    data['access_token'] = token.split("=")[1]

    data['provider'] = 'facebook'
    data['provider_id'] = data['id']

    data['success'] = True
    return data


@app.route('/disconnect')
def disconnect():
    """Disconnects user"""
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        return createJSONResponse('Current user not connected.', 401)

    if login_session['provider'] == 'google':
        url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
               % access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
    else:
        provider_id = login_session['provider_id']
        url = ('https://graph.facebook.com/v2.2/%s/permissions?'
               'access_token=%s') % (provider_id, access_token)
        print url
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['state']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['access_token']
        del login_session['provider']
        del login_session['provider_id']
        del login_session['user_id']

        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        return createJSONResponse('Failed to revoke token for given user.',
                                  400)


def createJSONResponse(msg, errorCode):
    """Helper function to create JSON response"""
    response = make_response(json.dumps(msg), errorCode)
    response.headers['Content-Type'] = 'application/json'
    return response


def createUser(login_session):
    """Creates a new user in the database

    Returns:
        id of the newly created user
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Fetches user from the databse by id
    Args:
        user_id: id of the user
    Returns:
        User object corresponding the given id
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Returns user id by the given email"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def userAllowed(user_id=None):
    """Check whether user is allowed in the system

    Args:
        user_id: id of the user who created the item in the page
    """
    if user_id is None:
        return 'user_id' in login_session
    else:
        return ('user_id' in login_session and
                user_id == login_session['user_id'])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
