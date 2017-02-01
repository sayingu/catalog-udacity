from flask import Flask
from flask import request, render_template, redirect, url_for, make_response
from flask import jsonify, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Category, CategoryItem, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from functools import wraps

import json
import random
import string
import httplib2
import requests

app = Flask(__name__)

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('/var/www/udacity-catalog/client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.route('/catalog/json')
def catalogJson():
    """JSON Endpoint for all category list"""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/catalog/<int:category_id>/items/json')
def categoryItemsJson(category_id):
    """JSON Endpoint for all items in a category(category_id) list"""
    categoryItems = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in categoryItems])


@app.route('/catalog/<int:category_id>/item/<int:category_item_id>/json')
def categoryItemJson(category_id, category_item_id):
    """JSON Endpoint for an item"""
    categoryItem = session.query(CategoryItem).\
        filter_by(id=category_item_id).\
        one()
    return jsonify(CategoryItem=[categoryItem.serialize])


@app.route('/')
@app.route('/catalog')
def catalogHtml():
    """Main catalog page includes categories, lastest 10 items"""

    # categories list for left
    categories = session.query(Category).order_by(asc(Category.name)).all()

    categoryItems = session.query(CategoryItem).\
        options(joinedload(CategoryItem.category)).\
        order_by(desc(CategoryItem.id)).\
        limit(10).\
        all()
    return render_template('main.html',
                           categories=categories,
                           categoryItems=categoryItems)


@app.route('/catalog/<int:category_id>/items')
def categoryItemsHtml(category_id):
    """Items page for specific category"""

    # categories list for left
    categories = session.query(Category).order_by(asc(Category.name)).all()

    category = session.query(Category).filter_by(id=category_id).one()
    categoryItems = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return render_template('category_items.html',
                           categories=categories,
                           category=category,
                           categoryItems=categoryItems)


@app.route('/catalog/<int:category_id>/new_item', methods=['GET', 'POST'])
@login_required
def newCategoryItemHtml(category_id):
    """New item page(get), add(post) for specific category"""
    if request.method == 'POST':
        newCategoryItem = CategoryItem(
            title=request.form['title'],
            description=request.form['description'],
            category_id=request.form['category_id'],
            user_id=login_session.get('user_id'))
        session.add(newCategoryItem)
        session.commit()

        flash('New Menu %s Item Successfully Created' %
              (newCategoryItem.title))

        return redirect(url_for('categoryItemsHtml', category_id=category_id))
    else:
        # categories list for left
        categories = session.query(Category).order_by(asc(Category.name)).all()

        return render_template('category_item_modify.html',
                               categories=categories,
                               category_id=category_id)


@app.route('/catalog/<int:category_id>/item/<int:category_item_id>')
def categoryItemHtml(category_id, category_item_id):
    """item page"""

    # categories list for left
    categories = session.query(Category).order_by(asc(Category.name)).all()

    categoryItem = session.query(CategoryItem).\
        filter_by(id=category_item_id).\
        one()
    return render_template('category_item.html',
                           categories=categories,
                           categoryItem=categoryItem)


@app.route('/catalog/<int:category_id>/item/<int:category_item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editCategoryItemHtml(category_id, category_item_id):
    """Edit item page(get), edit(post)"""
    categoryItem = session.query(CategoryItem).filter_by(
        id=category_item_id).one()

    if login_session.get('user_id') != categoryItem.user_id:
        rtnStr = "<script>function myFunction() {"
        rtnStr += "alert('You are not authorized to edit this item. "
        rtnStr += "Please create your own item in order to edit.');"
        rtnStr += "}</script><body onload='myFunction()'>"
        return rtnStr

    if request.method == 'POST':
        categoryItem.title = request.form['title']
        categoryItem.description = request.form['description']
        categoryItem.category_id = request.form['category_id']

        flash('%s Item Successfully Edited' % (categoryItem.title))

        return redirect(url_for('categoryItemHtml',
                                category_id=category_id,
                                category_item_id=category_item_id))
    else:
        # categories list for left
        categories = session.query(Category).order_by(asc(Category.name)).all()

        return render_template('category_item_modify.html',
                               categories=categories,
                               category_id=category_id,
                               category_item_id=category_item_id,
                               categoryItem=categoryItem)


@app.route('/catalog/<int:category_id>/item/<int:category_item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategoryItemHtml(category_id, category_item_id):
    """Delete item page(get), delete(post)"""
    categoryItem = session.query(CategoryItem).filter_by(
        id=category_item_id).one()

    if login_session.get('user_id') != categoryItem.user_id:
        rtnStr = "<script>function myFunction() {"
        rtnStr += "alert('You are not authorized to delete this item. "
        rtnStr += "Please create your own item in order to delete.');"
        rtnStr += "}</script><body onload='myFunction()'>"
        return rtnStr

    if request.method == 'POST':
        session.delete(categoryItem)

        flash('%s Item Successfully Deleted' % (categoryItem.title))

        session.commit()

        return redirect(url_for('categoryItemsHtml', category_id=category_id))
    else:
        # categories list for left
        categories = session.query(Category).order_by(asc(Category.name)).all()

        return render_template('category_item_delete.html',
                               categories=categories,
                               category_id=category_id,
                               category_item_id=category_item_id)


@app.route('/login')
def loginHtml():
    """login page for google plus"""
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
        oauth_flow = flow_from_clientsecrets('/var/www/udacity-catalog/client_secrets.json', scope='')
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; '
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print login_session.get('credentials')
    return output


@app.route('/disconnect')
def disconnect():
    """Excute disconnect google plus and delete session value"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            #del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('catalogHtml'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalogHtml'))


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
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    """Helper class for create user"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Helper class for get user"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Helper class for get user id from user email"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    #commented because use mod_wsgi for project 5
    #app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=80)
