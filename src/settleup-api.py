#!/usr/bin/env python

from bottle import route, run, template, Bottle
from bottle import get, post, request, response, redirect
from bottle import static_file

from settleup import *

from datetime import datetime
import time
import sys

app = Bottle()

@app.route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='static')

@app.route('/', method='GET')
def index():
	"""group chooser page"""
	db = settleupDB()
	group_ids = db.get_groups()
	print(group_ids)
	group_info = {g : db.get_group_users(g) for g in group_ids}
	print(group_info)
	return template("templates/choosegroup", groups=group_info)

@app.route('/', method='POST')
def index():
	"""set group cookie and redirect to new bill page"""
	group_id = request.forms.get('group')
	response.set_cookie('group',group_id)
	# redirect to newBill endpoint
	return """<script> window.location.replace("newBill"); </script>"""
	#return template("templates/redirect_newbill")
	#redirect("/newBill")

@app.route('/newUser', method='POST')
def index():
	"""create new user.  returns the new user id"""
	db = settleupDB()
	name = request.forms.get('name')
	return json.dumps(db.new_user(name))

@app.route('/newGroup', method='GET')
def index():
	"""create new group."""
	db = settleupDB()
	return "This feature is not yet implemented!"

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

@app.route('/newBill', method='GET')
def index():
	db = settleupDB()
	if request.get_cookie('group'):
		group_id = request.get_cookie('group')
	else:
		# redirect to group chooser if no group cookie
		return """<script> window.location.replace("/"); </script>"""
	users = db.get_group_users(group_id)
	top_user = db.get_top_user(group_id)
	history = db.get_group_history(group_id)
	return template("templates/newbill", today=datetime.today().strftime("%Y-%m-%d"), 
		group=group_id, users=users, top_user=top_user, history=history)

@app.route('/newBill', method='POST')
def index():
	"""create new bill.  returns the new bill id and order ids.
	For now, assume all bills are split equally
	parameters in the form:
		group -- group ID
		billDate
		paid -- who paid the bill  
		amount -- amount of bill
		notes
	order details are stored in the parameters order{i} in form {user_id}|{order_amount}|{amount_paid}"""
	db = settleupDB()

	# pull data out of the POST request
	if request.get_cookie('group'):
		group_id = request.get_cookie('group')
	else:
		# redirect to group chooser if no group cookie
		return """<script> window.location.replace("/"); </script>"""
	bill_date = request.forms.get('billDate')
	paid_uid = int(request.forms.get('paid'))
	amount = float(request.forms.get('amount'))
	notes = request.forms.get('notes')


	### split the order evenly
	orders = []
	users = db.get_group_users(group_id)
	for u in users:
		orders.append(order(u['user_id'],amount/len(users),amount if u['user_id']==paid_uid else 0))

	### use this code if the bill is split unevenly
	for u in request.forms.keys():
		if u[:5] == 'order':
			parsed_order = request.forms.get(u).strip().split('|')
			numerical_order = [int(parsed_order[0]),float(parsed_order[1]),float(parsed_order[2])]
			orders.append(order(*numerical_order))
	###

	# add new order to the DB
	result = db.new_bill(orders,bill_date,notes)

	# pull new data to display on the page
	new_users = db.get_group_users(group_id)
	new_history = db.get_group_history(group_id)
	top_user = db.get_top_user(group_id)

	return template("templates/newbill", today=datetime.today().strftime("%Y-%m-%d"), 
		group=group_id, users=new_users, top_user=top_user, history=new_history)


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
	if len(sys.argv) > 1 and sys.argv[1] == '-l':
		run(app, host='localhost', port=6543, reloader=True)
	else:
		run(app, host='0.0.0.0', port=6543)
