import MySQLdb
import MySQLdb.cursors
import json


class order(object):
	"""object to keep track of individual items in a bill"""
	def __init__(self,user_id,order_amount,amount_paid):
		self.user_id = user_id
		self.order_amount = order_amount
		self.amount_paid = amount_paid


class settleupDB(object):

	def __init__(self):
		self.db = MySQLdb.connect(user='root',db='settleup', cursorclass=MySQLdb.cursors.DictCursor)
		self.c = self.db.cursor()

	def new_user(self,username):
		self.c.execute("""INSERT INTO users (name) VALUES (%s);""", (username,))
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
		if sum([u.order_amount - u.amount_paid for u in orders]) != 0:
			raise ValueError('total amount ordered does not equal total amount paid')

		# insert a new bill into the table
		bill_total = sum([u.order_amount for u in orders])
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

	def delete_transaction(self,transaction_id):
		result = self.c.execute("""SELECT * FROM transactions WHERE transaction_id=%s;""", (transaction_id,))
		if result:
			row = self.c.fetchone()
			self.c.execute("""DELETE FROM transactions WHERE transaction_id=%s;""", (transaction_id,))
			self.c.execute("""UPDATE users SET total_borrowed = total_borrowed - %s WHERE user_id = %s;""", (row['amount'], row['borrower_id']))
			self.c.execute("""UPDATE users SET total_borrowed = total_borrowed + %s WHERE user_id = %s;""", (row['amount'], row['lender_id']))
			self.db.commit()
		return result



if __name__ == '__main__':

	#testing
	db = settleupDB()
	test_orders = [order(5,10,0),order(14,20,30)]
	