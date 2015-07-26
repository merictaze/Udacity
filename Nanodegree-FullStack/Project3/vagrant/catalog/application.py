from flask import Flask, render_template, url_for
from flask import request, redirect, flash, jsonify
from flask import session as login_session
from flask import make_response, Response

from flask.ext.seasurf import SeaSurf
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

from dict2xml import dict2xml as xmlify
import requests
import random
import string
import json
import os

from CatalogDAO import CatalogDAO
from CatalogHelper import *

app = Flask(__name__)
app.secret_key = 'cvAETf4adFASD4VDS4FB2fas43S5G4gth4T1'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

dao = CatalogDAO()
csrf = SeaSurf(app)


@app.route('/')
@app.route('/catalog/')
def catalog():
    """Shows the list of categories in the system"""
    categories = dao.getCategories()
    latestItems = dao.getLatestItems()
    return render_template('catalog.html', categories=categories,
                           latestItems=latestItems)


@app.route('/catalog/<int:category_id>/items')
def items(category_id):
    """Shows the list of items in the selected category

    Args:
        category_id: id of the category whose items will be shown in the page
    """
    category = dao.getCategory(category_id)
    items = dao.getItemsByCategory(category_id)
    return render_template('items.html', category=category, items=items)


@app.route('/catalog/<int:category_id>/item/<int:item_id>')
def item(category_id, item_id):
    """Shows the selected item and its information

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    category = dao.getCategory(category_id)
    item = dao.getItem(item_id)
    return render_template('item.html', category=category, item=item,
                           updateAllowed=createdByUser(item))


@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def itemEdit(category_id, item_id):
    """Lets user edit an item

    Only loggedin user who created the item can edit. Otherwise, user will be
    redirected to home page

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    item = dao.getItem(item_id)
    if not createdByUser(item):
        return redirect('/')

    data = {}
    if request.method == 'POST':
        if request.form['item_name']:
            data['name'] = request.form['item_name']
        if request.form['item_description']:
            data['description'] = request.form['item_description']
        if request.form['item_category']:
            data['category_id'] = request.form.getlist('item_category')[0]
        if request.form['item_img_url']:
            data['image'] = sendGETRequest(request.form['item_img_url'])[1]
        if request.files['item_image']:
            data['image'] = request.files['item_image'].read()
        dao.updateItem(item, data)
        flash('Item is updated successfully')
        return redirect(url_for('item', category_id=item.category_id,
                                item_id=item.id))
    else:
        categories = dao.getCategories()
        return render_template('item_edit.html', categories=categories,
                               item=item)


@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def itemDelete(category_id, item_id):
    """Lets user delete an item

    Only loggedin user who created the item can delete. Otherwise, user will be
    redirected to home page

    Args:
        category_id: id of the category of the item
        item_id: id of the item
    """
    item = dao.getItem(item_id)
    if not createdByUser(item):
        return redirect('/')

    if request.method == 'POST':
        dao.deleteItem(item_id)
        flash('Item "%s" is deleted successfully' % item.name)
        return redirect(url_for('items', category_id=category_id,
                                item_id=item_id))
    else:
        return render_template('item_delete.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def itemAdd():
    """Lets user add an item"""
    if request.method == 'POST':
        if (not request.form['item_name'] or
           not request.form['item_description'] or
           not request.form['item_category'] or
           not (request.files['item_image'] or request.form['item_img_url'])):
            flash('Please fill all the fields in the form')
        else:
            # get the image data either from the url or uploadted file
            if request.form['item_img_url']:
                imgData = sendGETRequest(request.form['item_img_url'])[1]
            else:
                imgData = request.files['item_image'].read()

            category = dao.getCategory(request.form['item_category'])
            dao.createItem(name=request.form['item_name'],
                           description=request.form['item_description'],
                           image=imgData,
                           user_id=login_session['user_id'],
                           category=category)

            flash('New item is added successfully')

    categories = dao.getCategories()
    return render_template('item_add.html', categories=categories)


@app.route("/images/<int:item_id>.jpg")
def getImage(item_id):
    """Serves images stored in the database"""
    item = dao.getItem(item_id)
    response = make_response(item.image)
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Content-Disposition'] = 'attachment; filename=img.jpg'
    return response


@app.route('/catalog/json')
def catalogJSON():
    """Returns catalog in JSON format"""
    categories = dao.getCategories()
    return jsonify(Catalog=[c.serialize(
                    dao.getItemsByCategory(c.id)) for c in categories])


@app.route('/catalog/xml')
def catalogXML():
    """Returns catalog in XML format"""
    categories = dao.getCategories()
    xml = xmlify({'category': [c.serialize(dao.getItemsByCategory(
                               c.id)) for c in categories]}, wrap="catalog")
    return Response(xml, mimetype='text/xml')


@app.route('/login')
def login():
    """Shows the login form"""
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@csrf.exempt
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
    user_id = dao.getUserID(login_session['email'])
    if not user_id:
        user_id = dao.createUser(login_session)
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

    result = json.loads(sendGETRequest(url)[1].decode('utf-8'))
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
    result = sendGETRequest(url)[1]

    # Use token to get user info from API
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?fields=id,name,email&%s' % token
    result = sendGETRequest(url)[1]
    data = json.loads(result)

    # Get user picture
    url = ('https://graph.facebook.com/v2.2/me/picture?%s'
           '&redirect=0&height=200&width=200') % token
    result = sendGETRequest(url)[1]
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
        result = sendGETRequest(url)[0]
    else:
        provider_id = login_session['provider_id']
        url = ('https://graph.facebook.com/v2.2/%s/permissions?'
               'access_token=%s') % (provider_id, access_token)
        result = sendDELETERequest(url)[0]

    # Reset the user's session.
    if 'user_id' in login_session:
        del login_session['state']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['access_token']
        del login_session['provider']
        del login_session['provider_id']
        del login_session['user_id']

    return redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
