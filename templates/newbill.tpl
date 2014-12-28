<!DOCTYPE html>
<!-- saved from url=(0069)https://www.etsy.com/join?ref=hdr&from_page=https://www.etsy.com/cart -->
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:og="http://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>SettleUp - New Bill</title>
    <!--
	<meta name="js_dist_path" content="/assets/dist/js/">
	<meta name="css_dist_path" content="/assets/dist/css/">
	<meta name="dist" content="201412231419373086">
    -->

   	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <link rel="stylesheet" href="/static/base.css" type="text/css">
    <link rel="stylesheet" href="/static/index.css" type="text/css">
    <link rel="stylesheet" href="/static/login.css" type="text/css">
    <link rel="stylesheet" href="/static/calculated-shipping.css" type="text/css">

    
</head>

<body class="mobile is-responsive  guest  iphone en-US new_header is-global-nav is-touch" data-clearable-enabled="true">

<h1>It's {{top_user['name']}}'s turn to pay!</h1>

	% for u in users:	
		<p>{{u['name']}} {{'owes' if u['total_borrowed'] >= 0 else 'is owed'}} ${{"%.0f" % abs(u['total_borrowed'])}}</p>
	% end

<hr>
<h2> New Bill </h2>
	<form id="billInfo" method="post" action="newBill">

	<table>

		<input type="hidden" name="group" value="{{group}}">
 		<tr>
		  	<td>Bill date:</td>	
	    	<td><input type="date" name="billDate" value="{{today}}"></td>
	    </tr>
	    <tr>
	    	<td>Who paid:</td>
	    	<td><select name="paid">
	    	  % for u in users:
				  <option value="{{u['user_id']}}" {{'selected="selected"' if u['user_id']==top_user['user_id'] else ''}}>{{u['name']}}</option>
			  % end
			</select></td>
		</tr>
		<tr>
			<td>Amount:</td>
			<td><input type="number" name="amount" min="0"></td>
		</tr>
		<tr>
			<td>Notes:</td>
			<td><input type="text" name="notes"></td>
		</tr>
	</table>
    		<button type="submit" form="billInfo" class="green">
              Split It!
            </button>
</form>

<hr>
<h2> Group History </h2>

<table cellpadding=20>
	<tr>
		<td>Date</td>
		<td>Bill Amount</td>
		<td>Paid By</td>
		<td>Notes</td>
	</tr>
	% for h in history:
	<tr>
		<td>{{h['bill_date']}}</td>
		<td align=right>{{"%.2f" % h['bill_amount']}}</td>
		<td>{{h['paid_by']}}</td>
		<td>{{h['notes']}}</td>
	</tr>
	% end
</table>


</body></html>