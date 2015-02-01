#!/usr/bin/env python

from bottle import route, run, template, Bottle
from bottle import get, post, request, response, redirect
from bottle import static_file

from settleup import *

from MySQLdb import escape_string
from datetime import datetime
import time
import sys

app = Bottle()

@app.route('/styles/<filename>')
def server_static(filename):
	return static_file(filename, root='styles')

@app.route('/', method='GET')
def index():
	"""group chooser page"""
	db = settleupDB()
	group_ids = db.get_groups()
	group_info = {g : db.get_group_users(g) for g in group_ids}
	return template("templates/choosegroup", groups=group_info)

@app.route('/getAllGroups', method='GET')
def index():
	"""JSON endpoint for all user/group info"""
	db = settleupDB()
	group_ids = db.get_groups()
	group_info = {g : db.get_group_users(g) for g in group_ids}
	return json.dumps(group_info)

@app.route('/chooseGroup', method='POST')
def index():
	"""set group cookie and redirect to new bill page"""
	group_id = request.forms.get('group')
	response.set_cookie('group',group_id)
	# redirect to newBill endpoint
	return """<script> window.location.replace("newBill"); </script>"""

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
	if request.query.get('group'):
		group_id = request.query.get('group')
	elif request.get_cookie('group'):
		group_id = request.get_cookie('group')
	else:
		# redirect to group chooser if no group cookie
		return """<script> window.location.replace("/"); </script>"""
	users = db.get_group_users(group_id)
	top_user = db.get_top_user(group_id)
	history = db.get_group_history(group_id)
	return template("templates/newbill", today=datetime.today().strftime("%Y-%m-%d"), 
		group=group_id, users=users, top_user=top_user, history=history)

@app.route('/groupData', method='GET')
def index():
	"""JSON endpoint returning data for the given group.
	   Group ID comes from either a 'group' cookie or a 'group' query parameter.  Query parameter gets priority."""
	if request.query.get('group'):
		group_id = request.query.get('group')
	elif request.get_cookie('group'):
		group_id = request.get_cookie('group')
	else:
		return """{"Error":"Must pass group ID via cookie or query parameter."}"""

	db = settleupDB()
	users = db.get_group_users(group_id)
	history = db.get_group_history(group_id)
	return json.dumps({'group':group_id, 'users':users, 'history':history})

@app.route('/newBill', method='POST')
def index():
	"""create new bill.  returns the new bill id and order ids.
	For now, assume all bills are split equally
	parameters in the form:
		group -- group ID
		billDate
		paid -- who paid the bill
		evensplit -- true if bill is split evenly, else missing
		amount -- amount of bill, when it's split evenly
		amount-{user_id} -- share of bill belonging to specified user
		notes
	order details are stored in the parameters order{i} in form {user_id}|{order_amount}|{amount_paid}"""
	db = settleupDB()

	# pull data out of the POST request
	if request.forms.get('group'):
		group_id = request.forms.get('group')
	elif request.get_cookie('group'):
		group_id = request.get_cookie('group')
	else:
		# redirect to group chooser if no group cookie or form value
		return """<script> window.location.replace("/"); </script>"""
	users = db.get_group_users(group_id)

	response_type = request.forms.get('response')
	if response_type not in ['html','json']:
		return """Error: Response parameter must be html or json."""

	bill_date = request.forms.get('billDate')
	paid_uid = int(request.forms.get('paid'))
	notes = escape_string(request.forms.get('notes'))

	# compute each user's share
	user_amounts = {}
	try:
		if request.forms.get('evensplit') == "True":
			# split bill evenly among all users
			amount = parse_amount(request.forms.get('amount'))
			for u in users:
				user_amounts[u['user_id']] = amount/len(users)
		else: # if request.forms.get('evensplit') == "False":
			# get each user's share from form data
			for u in users:
				user_amounts[u['user_id']] = parse_amount(request.forms.get('amount-'+str(u['user_id'])))
			amount = sum(user_amounts.values())
	except ValueError:
		return """Error: Amounts entered must be numeric."""
	print user_amounts
	print amount

	# create order objects
	orders = []
	for u in users:
		# order object takes (user_id, user_share, amount_paid)
		orders.append(order(u['user_id'], user_amounts[u['user_id']], amount if u['user_id']==paid_uid else 0))

	# add new order to the DB
	result = db.new_bill(orders,bill_date,notes)

	# pull new data to display on the page
	new_users = db.get_group_users(group_id)
	new_history = db.get_group_history(group_id)
	top_user = db.get_top_user(group_id)
	new_bill = db.get_bill(result['bill_id'])

	if response_type=='html':
		return template("templates/newbill", today=datetime.today().strftime("%Y-%m-%d"), 
			group=group_id, users=new_users, top_user=top_user, history=new_history)
	elif response_type=='json':
		return json.dumps({'new_bill':new_bill, 'users':new_users})
	else:
		raise Exception("Invalid response type found after DB update.") 


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
