<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:og="http://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>SettleUp - New Bill</title>

   	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <link rel="stylesheet" href="/styles/base.css" type="text/css">

    
</head>

<body class="mobile is-responsive  guest  iphone en-US new_header is-global-nav is-touch" data-clearable-enabled="true">



<h2>It's {{top_user['name']}}'s turn to pay!</h2>

<h1> Current Tab </h1>

<table class="current_tab">
	% for u in users:	
		<tr><td>{{u['name']}} {{'borrowed' if u['total_borrowed'] >= 0 else 'lent'}} ${{"%.0f" % abs(u['total_borrowed'])}}</td></td>
	% end
</table>

<h1> New Bill </h1>
	<form id="billInfo" method="post" action="newBill">

	<table>

		<input type="hidden" name="group" value="{{group}}">
		<input type="hidden" name="response" value="json">
		<input placeholder="Date" type="date" name="billDate" value="{{today}}" /><br />
    	<select name="paid">
	    	  % for u in users:
				  <option value="{{u['user_id']}}" {{'selected="selected"' if u['user_id']==top_user['user_id'] else ''}}>{{u['name']}}</option>
			  % end
		</select><br />
		<input placeholder="Amount" type="number" name="amount" min="0" /><br />
		<input placeholder="Notes" type="text" name="notes" /><br />
   		<button type="submit" form="billInfo" class="green">
              Split It!
        </button>
</form>


<table class="history_table">
	<tbody>
	<tr class="first_row">
		<th>Date</th>
		<th>Amount</th>
		<th>Paid By</th>
		<th>Notes</th>
	</tr>
	% for h in history:
	<tr>
		<td>{{h['bill_date']}}</td>
		<td class="amount">{{"%.2f" % h['bill_amount']}}</td>
		<td>{{h['paid_by']}}</td>
		<td>{{h['notes']}}</td>
	</tr>
	% end
	</tbody>
</table>


</body></html>