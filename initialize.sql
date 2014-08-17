/*
sudo mysqld_safe --skip-grant-tables &
mysql -u root
*/

create database settleup;
use settleup;

drop table users;
create table users (user_id INT not null auto_increment primary key, 
	name VARCHAR(40) not null, 
	total_borrowed FLOAT not null DEFAULT 0, 
/* sign convention: if total_borrowed is positive, the user has borrowed more than she has lent.
   if total_borrowed is negative, she has lent more than she has borrowed. */
	created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	last_updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

drop table transactions;
create table transactions (transaction_id INT not null auto_increment primary key,
	lender_id INT not null,
	borrower_id INT not null,
	transaction_date DATE,
	amount FLOAT not null,
	notes VARCHAR(1024),
	created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
	last_updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



/* sample commands:
insert into users (name) values ('dave');
update users set current_balance= current_balance + 1  where name='dave';
insert into transactions (lender_id, borrower_id, transaction_date, amount, notes) values (1,2,'2014-08-15', 3.45, 'test')
*/