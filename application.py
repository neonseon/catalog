from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, ApiCategory, Api, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from slugify import slugify

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Fun API Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///api.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
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
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                   'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: '
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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
    except LookupError:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                   'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API Endpoint
@app.route('/catalog.json')
def apiCategoriesJSON():
    api_categories = session.query(ApiCategory).options(joinedload(
                     ApiCategory.offerings)).all()
    return jsonify(api_categories=[dict(a.serialize,
                   offerings=[i.serialize for i in a.offerings])
                   for a in api_categories])


# Show all API categories
@app.route('/')
@app.route('/catalog/')
def showApiCategories():
    api_categories = session.query(ApiCategory).order_by(asc(ApiCategory.id))
    if 'username' not in login_session:
        return render_template('public-api-categories.html',
                               api_categories=api_categories)
    else:
        return render_template('api-categories.html',
                               api_categories=api_categories)


# Show an API Category
@app.route('/catalog/<api_category_slug>/')
@app.route('/catalog/<api_category_slug>/apis/')
def showApiCategory(api_category_slug):
    api_category = session.query(ApiCategory).filter_by(
                   slug=api_category_slug).one()
    apis = session.query(Api).filter_by(category_id=api_category.id).all()
    if 'username' not in login_session:
        return render_template('public-api-category.html', apis=apis,
                               api_category=api_category,
                               category_id=api_category.id)
    else:
        return render_template('api-category.html', apis=apis,
                               api_category=api_category,
                               category_id=api_category.id)


# Show an API
@app.route('/catalog/<api_category_slug>/<api_title_slug>/')
def showApi(api_category_slug, api_title_slug):
    api = session.query(Api).filter_by(slug=api_title_slug).one()
    api_category = session.query(ApiCategory).filter_by(
                   id=api.category_id).one()
    creator = getUserInfo(api.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('public-api.html', api=api,
                               api_category_name=api_category.name,
                               creator=creator)
    else:
        return render_template('api.html', api=api,
                               api_category_name=api_category.name,
                               creator=creator)


# Create a new API
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newApi():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newApi = Api(title=request.form['title'],
                     description=request.form['description'],
                     url=request.form['url'],
                     slug=slugify(request.form['title']),
                     category_id=request.form['category'],
                     user_id=login_session['user_id'])
        session.add(newApi)
        session.commit()
        flash('%s Successfully Created' % (newApi.title))
        return redirect(url_for('showApiCategories'))
    else:
        return render_template('newapi.html')


# Edit an API
@app.route('/catalog/<api_title_slug>/edit/', methods=['GET', 'POST'])
def editApi(api_title_slug):
    if 'username' not in login_session:
        return redirect('/login')
    editedApi = session.query(Api).filter_by(slug=api_title_slug).one()
    if login_session['user_id'] != editedApi.user_id:
        return "<script>function myFunction() {alert('You are not \
        authorized to edit this API. Please create your own \
        API in order to have editing privileges.');}\
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['title']:
            editedApi.title = request.form['title']
            editedApi.slug = slugify(request.form['title'])
        if request.form['description']:
            editedApi.description = request.form['description']
        if request.form['url']:
            editedApi.url = request.form['url']
        if request.form['category']:
            editedApi.category_id = request.form['category']
        session.add(editedApi)
        session.commit()
        flash('%s Successfully Edited' % (editedApi.title))
        return redirect(url_for('showApiCategories'))
    else:
        return render_template('editapi.html', api=editedApi)


# Delete an API
@app.route('/catalog/<api_title_slug>/delete/', methods=['GET', 'POST'])
def deleteApi(api_title_slug):
    if 'username' not in login_session:
        return redirect('/login')
    apiToDelete = session.query(Api).filter_by(slug=api_title_slug).one()
    if login_session['user_id'] != apiToDelete.user_id:
        return "<script>function myFunction() {alert('You are not \
        authorized to delete this API. Please create your own API \
        in order to have delete privileges.');}</script>\
        <body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(apiToDelete)
        session.commit()
        flash('API Successfully Deleted')
        return redirect(url_for('showApiCategories'))
    else:
        return render_template('deleteapi.html', api=apiToDelete)


# Disconnect based on provider, currently supporting Google
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showApiCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showApiCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
