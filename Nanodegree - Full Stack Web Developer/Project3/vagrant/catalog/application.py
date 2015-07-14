from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatalogItem
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)
app.secret_key = 'cvAETf4adFASD4VDS4FB2fas'

CLIENT_ID = "370251165587-11o4388lvlq6kmqp2o85im8ms1041f4d.apps.googleusercontent.com"
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).all()
    print categories
    return render_template('catalog.html', categories=categories)

@app.route('/catalog/<int:category_id>/items')
def items(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(CatalogItem).filter_by(category_id=category.id)
    return render_template('items.html', category=category, items=items)

@app.route('/catalog/<int:category_id>/item/<int:item_id>')
def item(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(CatalogItem).filter_by(category_id=category.id, id=item_id).one()
    return render_template('item.html', category=category, item=item)

@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit', methods=['GET','POST'])
def itemEdit(category_id, item_id):
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    print "*********",item_id,item.id
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
        print "*********",item_id,item.id
        return redirect(url_for('item', category_id=item.category_id, item_id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template('item_edit.html', categories=categories, item=item)

@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete', methods=['GET','POST'])
def itemDelete(category_id, item_id):
    item = session.query(CatalogItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item "%s" is deleted successfully' % item.name)
        return redirect(url_for('items', category_id=category_id, item_id=item_id))
    else:
        return render_template('item_delete.html', item=item)

@app.route('/login')
def login():
    # anti-forgery space token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    return redirect(url_for('catalog'))

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
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
        del login_session['credentials']
        del login_session['gplus_id']
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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)