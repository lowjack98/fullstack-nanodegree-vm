from database_setup import Base, Category, CatItem, User
from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify
from flask import make_response
from flask import session as login_session
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import httplib2
import json
import random
import requests
import string
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def verify_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in login_session:
            flash("You must be logged in for that action.", "alert-danger")
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


def verify_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in login_session:
            flash("You must be logged in for that action.", "alert-danger")
            return redirect(url_for('showLogin'))
        auth_user = session.query(User).filter_by(auth_id=login_session['auth_id']).first()
        if not auth_user:
            flash("You are not a registered user.", "alert-danger")
            return redirect(url_for('registerUser'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login-form.html', STATE=state, user=login_session)


@app.route('/register', methods=['GET', 'POST'])
@verify_login
def registerUser():
    # Show update form for GET
    # auth_user = session.query(User).filter_by(auth_id=login_session['auth_id']).first()
    if request.method == 'POST':
        newUser = User(auth_id=login_session['auth_id'],
                       name=login_session['username'],
                       email=login_session['email'])
        session.add(newUser)
        session.commit()
        flash("You are now registered!", "alert-success")
        return redirect(url_for('showCategories'))
    else:
        flash("To register click Register below.", "alert-success")
        return render_template('signup-form.html', user=login_session)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    #if request.args.post('state') != login_session['state']:
    if request.form['state'] != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    #code = request.data
    code = request.form['data']

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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
    #login_session['credentials'] = credentials.to_json()
    #print "credentials: "+credentials.to_json()+"\n"
    login_session['gplus_id'] = gplus_id
    print "gplus_id: "+gplus_id+"\n"
    login_session['access_token'] = credentials.access_token

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': login_session['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print "user data: "+json.dumps(data)+"\n"

    # Store user data in session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['auth_id'] = data['id']

    # if user doesn't exist in db reroute to signup page
    auth_user = session.query(User).filter_by(auth_id=login_session['auth_id']).first()
    if not auth_user:
        flash("You are not a registered user.", "alert-danger")
        return redirect(url_for('registerUser'))

    # Otherwise complete login
    return redirect(url_for('showCategories'))


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # clear user data from session
        #del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['access_token']
        flash("Successfully Logged Out.", "alert-success")
        return redirect(url_for('showCategories'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
def showCategories():
    # Show list of categories
    categories = session.query(Category).all()
    items = session.query(CatItem).order_by(CatItem.id.desc()).limit(10)
    return render_template('home.html', categories=categories, items=items,
                           user=login_session)


@app.route('/catalog/new', methods=['GET', 'POST'])
@verify_auth
def createCategory():
    # Show add form for GET
    # Add record on POST
    if request.method == 'POST':
        # redirect to home add status
        newCat = Category(name=request.form['catTitle'],
                          description=request.form['catDesc'])
        session.add(newCat)
        session.commit()
        flash("new category created!", "alert-success")
        return redirect(url_for('showCategories'))
    else:
        return render_template('catcreate.html', user=login_session)


@app.route('/catalog/<int:category_id>/edit', methods=['GET', 'POST'])
@verify_auth
def updateCategory(category_id):
    # Show update form for GET
    # Update record on POST
    editedCat = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['catTitle']:
            editedCat.name = request.form['catTitle']
        if request.form['catDesc']:
            editedCat.description = request.form['catDesc']
        session.add(editedCat)
        session.commit()
        flash("category updated!", "alert-success")
        return redirect(url_for('showCategories'))
    else:
        return render_template('catupdate.html', category=editedCat,
                               user=login_session)


@app.route('/catalog/<int:category_id>/delete', methods=['GET', 'POST'])
@verify_auth
def deleteCategory(category_id):
    # Show delete form for GET
    # Remove record on POST
    deletedCat = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(deletedCat)
        session.commit()
        flash("category removed!", "alert-success")
        return redirect(url_for('showCategories'))
    else:
        itemCnt = session.query(func.count(CatItem.id)).\
                          filter_by(category_id=category_id).scalar()
        return render_template('catdelete.html', category=deletedCat,
                               user=login_session, item_cnt=itemCnt)


@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showCatItems(category_id):
    # Show list of items for specific category
    categories = session.query(Category).all()
    items = session.query(CatItem).filter_by(category_id=category_id).all()
    return render_template('showitems.html', category_id=category_id,
                           categories=categories, items=items,
                           user=login_session)


@app.route('/catalog/<int:category_id>/items/<int:item_id>')
def showCatItemDetail(category_id, item_id):
    # Show item details
    item = session.query(CatItem).filter_by(id=item_id).one()
    return render_template('itemdetail.html', item=item, user=login_session)


@app.route('/catalog/<int:category_id>/items/new', methods=['GET', 'POST'])
@verify_auth
def createCatItem(category_id):
    # Show add form for GET
    # Add record on POST
    categories = session.query(Category).all()
    if request.method == 'POST':
        newCatItem = CatItem(name=request.form['itemName'],
                             description=request.form['itemDesc'],
                             category_id=request.form['itemCatId'])
        session.add(newCatItem)
        session.commit()
        flash("new item created!", "alert-success")
        items = session.query(CatItem).filter_by(category_id=category_id).all()
        return redirect(url_for('showCatItems', category_id=category_id))
    else:
        return render_template('itemcreate.html', categories=categories,
                               category_id=category_id, user=login_session)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@verify_auth
def editCatItem(category_id, item_id):
    # Show update form for GET
    # Update record on POST
    categories = session.query(Category).all()
    updatedCatItem = session.query(CatItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['itemName']:
            updatedCatItem.name = request.form['itemName']
        if request.form['itemDesc']:
            updatedCatItem.description = request.form['itemDesc']
        if request.form['itemCatId']:
            updatedCatItem.category_id = request.form['itemCatId']
        session.add(updatedCatItem)
        session.commit()
        flash("category item updated!", "alert-success")
        items = session.query(CatItem).filter_by(category_id=category_id).all()
        return redirect(url_for('showCatItems', category_id=category_id))
    else:
        return render_template('itemupdate.html', categories=categories,
                               category_id=category_id, item=updatedCatItem,
                               user=login_session)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
@verify_auth
def deleteCatItem(category_id, item_id):
    # Show delete form for GET
    # Remove record on POST
    deletedCatItem = session.query(CatItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(deletedCatItem)
        session.commit()
        flash("item removed!", "alert-success")
        return redirect(url_for('showCatItems', category_id=category_id))
    else:
        return render_template('itemdelete.html', item=deletedCatItem,
                               user=login_session)


@app.route('/catalog/JSON')
def showCategoriesJson():
    # show json string with all categories
    categories = session.query(Category).all()
    return jsonify(Catagories=[i.serialize for i in categories])


@app.route('/catalog/<int:category_id>/JSON')
def showCatDetailJson(category_id):
    # show json string with category details
    categories = session.query(Category).filter_by(id=category_id).one()
    return jsonify(category=categories.serialize)


@app.route('/catalog/<int:category_id>/items/JSON')
def showCatItemsJson(category_id):
    # show json string with all items for a category
    items = session.query(CatItem).filter_by(category_id=category_id).all()
    return jsonify(CatItems=[i.serialize for i in items])


@app.route('/catalog/<int:category_id>/items/<int:item_id>/JSON')
def showCatItemDetailJson(category_id, item_id):
    # show json string with item details
    items = session.query(CatItem).filter_by(
        category_id=category_id).filter_by(id=item_id).one()
    return jsonify(CatItem=items.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_ninja_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
