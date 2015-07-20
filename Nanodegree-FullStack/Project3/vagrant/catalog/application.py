from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
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
app.secret_key = 'cvAETf4adFASD4VDS4FB2fas'

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalog():
    """Shows the list of categories in the system"""
    categories = session.query(Category).all()
    latestItems = session.query(CatalogItem).join(CatalogItem.category).order_by(CatalogItem.time_create.desc()).limit(10);
    return render_template('catalog.html', categories=categories, latestItems=latestItems)


@app.route('/catalog/<int:category_id>/items')
def items(category_id):
    """Shows the list of items in the category

    Args:
        category_id: id of the category whose items will be shown in the page
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id)
    return render_template('items.html', category=category, items=items)


@app.route('/catalog/<int:category_id>/item/<int:item_id>')
def item(category_id, item_id):
    """Shows the item and its information

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
    categories = session.query(Category)
    return jsonify([c.serialize for c in categories])
    #session.query(CatalogItem).filter_by(category_id=c.id).all()
    #return jsonify(Catalog=[c.serialize for c in categories])


@app.route('/login')
def login():
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state', '') != login_session['state']:
        return createResponse('Invalid state parameter.', 401)

    # Obtain authorization code
    auth_code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        #oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        return createResponse('Failed to upgrade the authorization code.', 401)

    login_session['credentials'] = credentials.to_json()




    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return redirect(url_for('catalog'))


@app.route('/gdisconnect')
def gdisconnect():
      # Reset the user's sesson.
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    # Only disconnect a connected user.
    credentials = AccessTokenCredentials(login_session.get('access_token'),
                                         'user-agent-value')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createResponse(msg, errorCode):
    response = make_response(json.dumps(msg), errorCode)
    response.headers['Content-Type'] = 'application/json'
    return response


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def userAllowed(user_id=None):
    if user_id == None:
        return 'user_id' in login_session
    else:
        return 'user_id' in login_session and user_id == login_session['user_id']


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)