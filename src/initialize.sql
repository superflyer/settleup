/*
sudo mysqld_safe --skip-grant-tables &
mysql -u root 

UPDATE mysql.user SET Password=PASSWORD('password') WHERE User='root';
FLUSH PRIVILEGES;
*/


create database settleup;
use settleup;

drop table users;
create table users (user_id INT not null auto_increment primary key, 
	group_id INT not null,
	name VARCHAR(40) not null, 
	total_borrowed FLOAT not null DEFAULT 0, 
/* sign convention: if total_borrowed is positive, the user has borrowed more than she has lent.
   if total_borrowed is negative, she has lent more than she has borrowed. */
/*	created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP, */
	last_updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
insert into users (group_id, name) values (0, 'Test User');

drop table bills;
create table bills (bill_id INT not null auto_increment primary key,
	bill_date DATE not null,
	bill_amount FLOAT not null,
	notes VARCHAR(1024),
/*	created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  */
	last_updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

drop table orders;
/* each bill is divided into one or more orders */
create table orders (order_id INT not null auto_increment primary key,
	bill_id INT not null,
	user_id INT not null,
	order_amount FLOAT not null,
	amount_paid FLOAT not null DEFAULT 0,
/*	created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  */
	last_updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);




/* sample commands:
insert into users (name) values ('dave');
update users set current_balance= current_balance + 1  where name='dave';
insert into transactions (lender_id, borrower_id, transaction_date, amount, notes) values (1,2,'2014-08-15', 3.45, 'test')
*/