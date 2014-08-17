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

@app.route('/newTransaction', method='POST')
def index():
	"""create new transaction.  returns the new transaction id"""
	db = settleupDB()
	lender_id = request.forms.get('lenderId')
	borrower_id = request.forms.get('borrowerId')
	transaction_date = request.forms.get('transactionDate')
	amount = request.forms.get('amount')
	notes = request.forms.get('notes')
	try:
		return json.dumps(db.new_transaction(lender_id,borrower_id,transaction_date,amount,notes))
	except ValueError as e:
		return '{"error": "' + str(e) + '"}'

@app.route('/getTransactions', method='GET')
def index():
	"""get info for n most recent transactions for given user ID.
	   gets transactions for all users if user ID is missing
	   gets all transactions if query param n is 0 or missing"""
	db = settleupDB()
	n = request.query.get('n')
	user_id = request.query.get('userId')
	return json.dumps(db.get_transactions(user_id,n))

@app.route('/deleteTransaction', method='POST')
def index():
	"""delete a transaction.  returns 1 if transaction is deleted, 0 otherwise."""
	db = settleupDB()
	transaction_id = request.forms.get('transactionId')
	return json.dumps(db.delete_transaction(transaction_id))




if __name__=='__main__':
	run(app, host='localhost', port=6543, reloader=True)
	run(app, host='0.0.0.0', port=6543)
