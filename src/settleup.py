#!/usr/bin/env python

import MySQLdb
import MySQLdb.cursors
import json
import re

class order(object):
	"""object to keep track of individual items in a bill"""
	def __init__(self,user_id,order_amount,amount_paid):
		self.user_id = user_id
		self.order_amount = order_amount
		self.amount_paid = amount_paid

	def __repr__(self):
		return '{id: '+str(self.user_id) + ', order_amount: '+str(self.order_amount) + ', amount_paid: '+str(self.amount_paid)+'}'

	def __str__(self):
		return self.__repr__()

class settleupDB(object):

	def __init__(self):
		self.db = MySQLdb.connect(user='root',db='settleup',passwd='password',cursorclass=MySQLdb.cursors.DictCursor)
		self.c = self.db.cursor()

	def new_group(self,users):
		"""create new group.  users is a list of user names (i.e. real names)."""
		self.c.execute("""SELECT MAX(group_id) FROM users;""")
		group_id = self.c.fetchone().values()[0]+1;
		results = []
		for name in users:
			results.append(self.new_user(group_id,name))
		return results

	def get_top_user(self,group_id):
		"""get the user who has paid the most"""
		self.c.execute("""SELECT user_id, name FROM users WHERE group_id=%s ORDER BY total_borrowed DESC LIMIT 1""", (group_id,))
		result = self.c.fetchone()
		return result

	def get_groups(self):
		"""get all groups IDS.  exclude test groups with ID <= 0"""
		self.c.execute("""SELECT DISTINCT group_id FROM users WHERE group_id > 0;""")
		results = self.c.fetchall()
		ids = [r['group_id'] for r in results]
		return ids

	def get_group_users(self,group_id):
		"""get users for a particular group"""
		self.c.execute("""SELECT user_id, name, total_borrowed FROM users WHERE group_id=%s ORDER BY total_borrowed DESC;""", (group_id,))
		results = self.c.fetchall()
		return results

	def new_user(self,group_id,username):
		self.c.execute("""INSERT INTO users (group_id,name) VALUES (%s,%s);""", (group_id,username,))
		self.c.execute("""SELECT MAX(user_id) as user_id FROM users;""")
		self.db.commit()
		result = self.c.fetchone()
		return result

	def get_user(self,user_id=None):
		if user_id:
			where = 'WHERE user_id='+str(user_id)
		else:
			where = ''
		self.c.execute("""SELECT user_id, name, total_borrowed, UNIX_TIMESTAMP(created_ts) as created_ts, 
			UNIX_TIMESTAMP(last_updated_ts) as last_updated_ts
			FROM users """ + where + ';')
		results = self.c.fetchall()
		if user_id:
			return results[0]
		else:
			return results		

	def delete_user(self,user_id):
		result = self.c.execute("""DELETE FROM users WHERE user_id=%s;""", (user_id,))
		self.db.commit()
		return result

	def new_bill(self,orders,bill_date,notes=None):
		""" Add a new bill to the DB.  
			orders is a list of order objects.
			Notes are optional."""

		results = {'order_ids':[]}

		# check input to make sure all parties are in the users DB
		for u in orders:
			self.c.execute("""SELECT COUNT(*) as num_matches FROM users where user_id = %s;""", (u.user_id,))
			if not self.c.fetchone()['num_matches']:
				raise ValueError('user ' + str(u.user_id) + ' is not in the users table')

		# check input to make sure amount ordered == amount paid
		print(orders)
		if abs(sum([u.order_amount - u.amount_paid for u in orders])) > 0.01:
			raise ValueError('total amount ordered does not equal total amount paid')

		bill_total = sum([u.order_amount for u in orders])

		# check to make sure this isn't a duplicate
		result = self.c.execute("""SELECT * FROM bills WHERE bill_date=%s AND bill_amount=%s and notes=%s;""",
			(bill_date, bill_total, notes))
		if result:
			raise ValueError('duplicate entry')

		# insert a new bill into the bills table
		self.c.execute("""INSERT INTO bills (bill_date, bill_amount, notes) 
			VALUES (%s,%s,%s);""", (bill_date, bill_total, notes))
		self.c.execute("""SELECT MAX(bill_id) as bill_id FROM bills;""")
		current_result = self.c.fetchone()
		current_bill = current_result['bill_id']
		results['bill_id'] = current_bill

		# insert each order into the orders table
		for u in orders:
			self.c.execute("""INSERT INTO orders (bill_id, user_id, order_amount, amount_paid) VALUES (%s,%s,%s,%s);""",
				(current_bill, u.user_id, u.order_amount, u.amount_paid))
			self.c.execute("""SELECT MAX(order_id) as order_id FROM orders;""")
			current_result = self.c.fetchone()
			current_order = current_result['order_id']
			results['order_ids'].append(current_order)

			# update balance for that user
			self.c.execute("""UPDATE users SET total_borrowed = total_borrowed + %s - %s WHERE user_id = %s;""",
				(u.order_amount, u.amount_paid, u.user_id))

		self.db.commit()

		return results

	def get_orders(self,user_id=None,n=0):
		"""get n most recent orders for the given user id"""
		if n > 0:
			limit = 'LIMIT ' + str(n)
		else:
			limit = ''
		if user_id:
			where = 'WHERE b.user_id=' + str(user_id)
		else:
			where = ''
		self.c.execute("""SELECT a.bill_id, CAST(a.bill_date as CHAR) as bill_date, a.notes, b.order_amount, b.amount_paid,
			UNIX_TIMESTAMP(b.created_ts) as created_ts, UNIX_TIMESTAMP(b.last_updated_ts) as last_updated_ts
			FROM bills a JOIN orders b on a.bill_id=b.bill_id """ + where + """ ORDER BY bill_date DESC """ + limit + ';')
		results = self.c.fetchall()
		return results	

	def get_bill(self,bill_id):
		"""get info for a specific bill"""
		self.c.execute("""SELECT CAST(a.bill_date as CHAR) as bill_date, a.bill_amount, c.name as paid_by, a.notes
			FROM bills a
				JOIN orders b on a.bill_id=b.bill_id
				JOIN users c on b.user_id=c.user_id
			WHERE a.bill_id=%s and b.amount_paid > 0;""", (bill_id,))
		results = self.c.fetchall()
		return results	

	def get_group_history(self,group_id,n=0):
		"""get n most recent bills for the given group, along with user who paid a non-negative amount.
		currently assumes all bills are split evenly with one user paying."""
		if n > 0:
			limit = 'LIMIT ' + str(n)
		else:
			limit = ''
		self.c.execute("""SELECT CAST(a.bill_date as CHAR) as bill_date, a.bill_amount, c.name as paid_by, a.notes
			FROM bills a
				JOIN orders b on a.bill_id=b.bill_id
				JOIN users c on b.user_id=c.user_id
			WHERE c.group_id=%s and b.amount_paid > 0 ORDER BY bill_date DESC """ + limit + ';', (group_id,))
		results = self.c.fetchall()
		return results


	def delete_bill(self,bill_id):
		# get orders for this bill from the orders table
		self.c.execute("""SELECT * FROM orders WHERE bill_id=%s;""", (bill_id,))
		orders = self.c.fetchall()

		# check to make sure there are results to delete
		if not orders:
			raise ValueError('Bill not found in the DB')

		# update balance for each user
		for u in orders:
			# update balance for that user
			self.c.execute("""UPDATE users SET total_borrowed = total_borrowed + %s - %s WHERE user_id = %s;""",
				(u['amount_paid'], u['order_amount'], u['user_id']))

		# delete orders from orders table
		self.c.execute("""DELETE FROM orders WHERE bill_id=%s;""", (bill_id,))

		# delete bill from bills table
		self.c.execute("""DELETE FROM bills WHERE bill_id=%s;""", (bill_id,))

		self.db.commit()
		return(orders);


def parse_amount(raw_amount):
	"""Parses a user-entered string into a decimal dollar amount 
		by stripping leading and trailing non-numerical characters."""
	if not raw_amount:
		return 0.0
	p = re.compile('^[^0-9]*([0-9]*\.?[0-9]*)[^0-9]*$')
 	m = p.match(raw_amount)
 	if not m:
 		raise ValueError
 	s = m.groups()[0]
 	if not s:
 		raise ValueError
 	if s == '.':
 		raise ValueError
	d = float(s)
	return d


if __name__ == '__main__':

	#testing
	db = settleupDB()
	test_orders = [order(5,10,0),order(14,20,30)]
	