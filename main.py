# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, request, session, redirect
from google.cloud import datastore
from google.oauth2 import id_token

import datetime
import sys
import requests

datastore_client = datastore.Client()
DEFAULT_KEY = 'action'
app = Flask(__name__)
app.secret_key = b'lkjadfsj009(*02347@!$&'
default_genres = set(["action", "platform", "puzzle", "role-playing", "sports"])

# Function to store game info of specific genre in datastore
def store_video_game(title, rating, platform, developer, year, price, username, email, dt, kn):
    entity = datastore.Entity(key = datastore_client.key(kn))
    entity.update({
        'title': title,
        'rating': rating,
        'platform': platform,
        'developer': developer,
        'year': year,
        'price': price,
        'timestamp': dt,
        'username': username,
        'email': email
    })

    datastore_client.put(entity)

# Function to add unique game in to the cart(a datastore "kind")
def add_unique_game_to_cart(title, rating, platform, developer, year, price, username, email, dt, kn):
    query = datastore_client.query(kind=kn)
    games = query.fetch()
    for game in games:
        if (game['title'] == title and game['rating'] == rating and game['platform'] == platform
            and game['developer'] == developer and game['year'] == year and game['price'] == price
            and game['username'] == username and game['email'] == email):
            return

    store_video_game(title, rating, platform, developer, year, price, username, email, dt, kn)

# Find the game of certain genre from datastore based on id
def find_game_by_id(genre, game_id):
    query = datastore_client.query(kind=genre)
    games = query.fetch()
    for game in games:
        if game.key.id == int(game_id):
            return game

# Fetch all the games in a given genre
def fetch_items(kn):
    query = datastore_client.query(kind=kn)
    query.order = ['-timestamp']
    games = query.fetch()
    return games

# Function to search the video of given genre according to one or more field
def search_video_game(title, rating, platform, developer, year, genre):
    query = datastore_client.query(kind = genre)
    games = query.fetch() 
    results = []
    for game in games:
        if (title != "" and game['title'].lower().find(title.lower()) == -1):
            continue
        if (rating != "" and game['rating'].lower().find(rating.lower()) == -1):
            continue
        if (platform != "" and game['platform'].lower().find(platform.lower()) == -1):
            continue
        if (developer != "" and game['developer'].lower().find(developer.lower()) == -1):
            continue
        if (year != "" and game["year"] != year):
            continue
        results.append(game)
    return results

# Function to find the user's games in cart or purchase history
def find_user_item(username, useremail, user_type):
    query = datastore_client.query(kind = user_type)
    items = query.fetch()
    results = []
    for item in items:
        if (item['username'] == username and item['email'] == useremail):
            results.append(item)
    return results

# Function to add the genres newly added to the 'added_genre' in data store
def add_unique_genre_to_app(game_type, dt):
    query = datastore_client.query(kind = 'added_genre')
    genres = query.fetch()
    for genre in genres:
        if (genre['name'] == game_type):
            return
    kn = 'added_genre'
    entity = datastore.Entity(key = datastore_client.key(kn))
    entity.update({
        'name': game_type,
        'timestamp': dt
    })
    datastore_client.put(entity)

# Home page
@app.route('/', methods=['GET', 'POST'])
def root():
    added_genres = fetch_items('added_genre') # Fetch the added genres
    return render_template(
        'index.html', genres=sorted(default_genres), added_genres = added_genres)

# Login
@app.route('/login', methods=['POST'])
def login():

    # Decode the incoming data
    token = request.data.decode('utf-8')
    # Send to google for verification and get JSON return values
    verify = requests.get("https://oauth2.googleapis.com/tokeninfo?id_token=" + token)
    # Use a session cookie to store the username and email
    session['username'] = verify.json()["name"]
    session['email'] = verify.json()["email"]

    return redirect("/")

# Add video game page
@app.route('/new', methods=['GET', 'POST'])
def new():
    key_name = DEFAULT_KEY
    if 'username' in session:
        username = session['username'] 
    else:
        username = ''
    if 'email' in session:
        useremail = session['email'] 
    else:
        useremail = ''
    # If POST, store the new message into Datastore in the appropriate genre
    if request.method == 'POST':
        key_name = request.form['genre'].strip().lower()
        store_video_game(request.form['title'].strip(), 
            request.form['rating'].strip(), 
            request.form['platform'].strip(), 
            request.form['developer'].strip(), 
            request.form['year'].strip(), 
            request.form['price'].strip(), 
            username, 
            useremail, 
            datetime.datetime.now(), 
            key_name)
        # If the added genre is not in the default, add it if unique
        if key_name not in default_genres:
            add_unique_genre_to_app(key_name, datetime.datetime.now())
        return redirect('/')

    return render_template('new.html')

# Search page
@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        genre = request.form['genre'].strip()
        title = request.form['title'].strip()
        rating = request.form['rating'].strip()
        platform = request.form['platform'].strip()
        developer = request.form['developer'].strip()
        year = request.form['year'].strip()
        # Error if no fields
        if (title == "" and rating == "" and platform == "" and developer == "" and year == ""):
            message = "Please at least input one field."
            return render_template('notfound.html', message=message)

        results = search_video_game(title, rating, platform, developer, year, genre)
        if (len(results) == 0):
            message = "Sorry, no game found."
            return render_template('notfound.html', message=message)

        return render_template('result.html', results = results, genre = genre)
    return render_template('search.html')

# Display a genre 
@app.route('/display/<genre>', methods=['GET'])
def display(genre):
    games = fetch_items(genre)
    return render_template('show.html', games = games, genre = genre)

# Add to user's cart
@app.route('/add', methods = ['GET','POST'])
def add_game():
    kind = request.args.get('kind')
    game_id = request.args.get('id')
    key_name = DEFAULT_KEY
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    # If not login
    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')

    game = find_game_by_id(kind, game_id)
    key_name = 'cart'
    add_unique_game_to_cart(game['title'].strip(), game['rating'].strip(), game['platform'].strip(), game['developer'].strip(), 
        game['year'].strip(), game['price'].strip(), username, useremail, datetime.datetime.now(), key_name)
    return redirect('/cart/'+ username)

# Cart
@app.route('/cart/', methods = ['GET'])
def cart():
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')
    return redirect('/cart/'+ username)

# To show user's cart
@app.route('/cart/<username>', methods = ['GET','POST'])
def user_cart(username):
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')

    # If there is no items in user's cart, do not show "Checkout"(ready = false)
    games = find_user_item(username, useremail, 'cart')
    if (len(games) == 0):
        ready = False
    else:
        ready = True

    price_sum = 0
    for game in games:
        price_sum += int(game['price'])

    return render_template('cart.html', games = games, username = username, sum = price_sum, ready = ready)

# Remove item from cart
@app.route('/remove/<cart_id>', methods = ['GET', 'POST'])
def remove_cart_item(cart_id):
    genre = 'cart'
    game = find_game_by_id(genre, cart_id)
    datastore_client.delete(game.key)
    return redirect('/cart/')

# Confirm to checkout
@app.route('/readytocheck', methods = ['GET'])
def ready():
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')

    games = find_user_item(username, useremail, 'cart')
    price_sum = 0
    for game in games:
        price_sum += int(game['price'])
    return render_template('ready.html', games = games, username = username, sum = price_sum)

# Checkout result
@app.route('/checkout', methods = ['GET'])
def checkout():
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')
    games = find_user_item(username, useremail, 'cart')
    price_sum = 0
    for game in games:
        price_sum += int(game['price'])
        datastore_client.delete(game.key)
        store_video_game(game['title'], game['rating'], game['platform'], game['developer'], 
            game['year'], game['price'], username, useremail, datetime.datetime.now(), 'purchase_history')
    return render_template('checkout.html', sum = price_sum, username = username)

# Purchase history
@app.route('/history/', methods = ['GET'])
def history():
    if 'username' in session:
        username = session['username'] 
    else:
        username = 'Anonymous'

    if 'email' in session:
        useremail = session['email']
    else:
        useremail = ''

    if username == 'Anonymous' and useremail == '':
        return render_template('noauthen.html')
    games = find_user_item(username, useremail, 'purchase_history')

    return render_template('history.html', games = games, username = username)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
