#!/usr/bin/env python

from bottle import route, run, template, Bottle
from bottle import get, post, request

from settleup import *

app = Bottle()


@app.route('/newUser', method='POST')
def index():
	"""create new user.  returns the new user id"""
	db = settleupDB()
	name = request.forms.get('name')
	return json.dumps(db.new_user(name))

@app.route('/getUser', method='GET')
def index():
	"""get info for a single user.
	   gets all users if query param userId is missing"""
	db = settleupDB()
	user_id = request.query.get('userId')
	return json.dumps(db.get_user(user_id))

@app.route('/deleteUser', method='POST')
def index():
	"""delete a user.  returns 1 if user is deleted, 0 otherwise."""
	db = settleupDB()
	user_id = request.forms.get('userId')
	return json.dumps(db.delete_user(user_id))

@app.route('/newBill', method='POST')
def index():
	"""create new bill.  returns the new bill id and order ids.  
	order details are stored in the parameters order{i} in form {user_id}|{order_amount}|{amount_paid}"""
	db = settleupDB()
	orders = []
	for u in request.forms.keys():
		if u[:5] == 'order':
			parsed_order = request.forms.get(u).strip().split('|')
			numerical_order = [int(parsed_order[0]),float(parsed_order[1]),float(parsed_order[2])]
			orders.append(order(*numerical_order))
	bill_date = request.forms.get('billDate')
	notes = request.forms.get('notes')
	try:
		return json.dumps(db.new_bill(orders,bill_date,notes))
	except ValueError as e:
		return '{"error": "' + str(e) + '"}'

@app.route('/getOrders', method='GET')
def index():
	"""get info for n most recent orders for given user ID.
	   gets orders for all users if user ID is missing
	   gets all orders if query param n is 0 or missing"""
	db = settleupDB()
	n = request.query.get('n')
	user_id = request.query.get('userId')
	return json.dumps(db.get_orders(user_id,n))

@app.route('/deleteTransaction', method='POST')
def index():
	"""delete a transaction.  returns 1 if transaction is deleted, 0 otherwise."""
	db = settleupDB()
	transaction_id = request.forms.get('transactionId')
	return json.dumps(db.delete_transaction(transaction_id))




if __name__=='__main__':
	run(app, host='localhost', port=6543, reloader=True)
	#run(app, host='0.0.0.0', port=6543)
