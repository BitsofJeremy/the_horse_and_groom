from flask import Flask, request, render_template, session, flash, redirect, url_for, make_response
from flask_restful import Resource, Api
from collections import Counter
import json
import os

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Load the beers.json file
with open('beers.json') as f:
    beers = json.load(f)

class Beer(Resource):
    def get(self, beer_id):
        beer = next((beer for beer in beers if beer['id'] == beer_id), None)
        if beer is None:
            return {'message': 'Beer not found'}, 404
        response = make_response(render_template('beer.html', beer=beer))
        response.headers['Content-Type'] = 'text/html'
        return response

class BeerList(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        return beers[offset: offset + limit]

class BeerSearch(Resource):
    def get(self):
        query = request.args.get('q')
        result = [beer for beer in beers if query.lower() in beer['name'].lower() or query.lower() in beer['description'].lower()]
        response = make_response(render_template('search.html', beers=result))
        response.headers['Content-Type'] = 'text/html'
        return response

class Cart(Resource):
    def get(self):
        cart = session.get('cart', [])
        item_counts = Counter(cart)
        items = [{'item': item, 'count': item_counts[str(item['id'])]} for item in beers if str(item['id']) in cart]
        total = sum(item['item']['price'] * item['count'] for item in items)
        response = make_response(render_template('cart.html', items=items, total=total))
        response.headers['Content-Type'] = 'text/html'
        return response

    def post(self):
        item_id = request.form.get('item_id')
        action = request.form.get('action')
        cart = session.get('cart', [])
        if action == 'add':
            cart.append(item_id)
            flash('Item added to cart')
        elif action == 'remove' and item_id in cart:
            cart.remove(item_id)
            flash('Item removed from cart')
        else:
            flash('Item not found in cart')
        session['cart'] = cart
        return redirect(url_for('cart'))

    def delete(self):
        item_id = request.form.get('item_id')
        cart = session.get('cart', [])
        if item_id in cart:
            cart.remove(item_id)
            session['cart'] = cart
            flash('Item removed from cart')
        else:
            flash('Item not found in cart')
        return redirect(url_for('cart'))

api.add_resource(Beer, '/beer/<int:beer_id>')
api.add_resource(BeerList, '/beers')
api.add_resource(BeerSearch, '/beers/search')
api.add_resource(Cart, '/cart')

@app.route('/')
def home():
    return render_template('index.html', beers=beers)

@app.route('/beers/<int:beer_id>')
def beer_detail(beer_id):
    beer = next((beer for beer in beers if beer['id'] == beer_id), None)
    return render_template('beer.html', beer=beer)

if __name__ == '__main__':
    app.run(debug=True)