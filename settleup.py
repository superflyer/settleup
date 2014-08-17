import MySQLdb
import MySQLdb.cursors
import json

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

	def new_transaction(self,lender_id,borrower_id,transaction_date,amount,notes=None):
		""" Add a transaction to the DB.  Notes are optional."""

		# check input to make sure both parties are in the users DB
		self.c.execute("""SELECT COUNT(*) as parties FROM users WHERE user_id IN (%s,%s);""", (int(lender_id),int(borrower_id)))
		parties = self.c.fetchone()['parties']
		if parties != 2:
			if lender_id == borrower_id:
				raise ValueError('borrower and lender must be distinct')
			else:
				raise ValueError('borrower or lender missing from users table')

		self.c.execute("""INSERT INTO transactions (lender_id, borrower_id, transaction_date, amount, notes) 
			VALUES (%s,%s,%s,%s,%s);""", (lender_id,borrower_id,transaction_date,amount,notes))

		# update balances
		self.c.execute("""UPDATE users SET total_borrowed = total_borrowed + %s WHERE user_id = %s;""", (amount, borrower_id))
		self.c.execute("""UPDATE users SET total_borrowed = total_borrowed - %s WHERE user_id = %s;""", (amount, lender_id))
		self.db.commit()

		# get id of new tranaction
		self.c.execute("""SELECT MAX(transaction_id) as transaction_id FROM transactions;""")
		result = self.c.fetchone()
		return result

	def get_transactions(self,user_id=None,n=0):
		"""get n most recent transactions for the given user id"""
		if n > 0:
			limit = 'LIMIT ' + str(n)
		else:
			limit = ''
		if user_id:
			where = 'WHERE lender_id=' + str(user_id) + ' OR borrower_id=' + str(user_id)
		else:
			where = ''
		self.c.execute("""SELECT transaction_id, lender_id, borrower_id, CAST(transaction_date as CHAR) as transaction_date,
			amount, notes, UNIX_TIMESTAMP(created_ts) as created_ts, 
			UNIX_TIMESTAMP(last_updated_ts) as last_updated_ts
			FROM transactions """ + where + """ ORDER BY transaction_date DESC """ + limit + ';')
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

	db = settleupDB()