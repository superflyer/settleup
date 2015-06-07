<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:og="http://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>WideOpenTab - New Bill</title>

   	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <link rel="stylesheet" href="/styles/base.css" type="text/css">


    <script type="text/javascript"><!--
		/* Script by: www.jtricks.com
		 * Version: 20090221
		 * Latest version:
		 * www.jtricks.com/javascript/blocks/showinghiding.html
		 */
		function showPageElement(what)
		{
		    var obj = typeof what == 'object'
		        ? what : document.getElementById(what);

		    obj.style.display = 'block';
		    return false;
		}

		function hidePageElement(what)
		{
		    var obj = typeof what == 'object'
		        ? what : document.getElementById(what);

		    obj.style.display = 'none';
		    return false;
		}

		function togglePageElementVisibility(what)
		{
		    var obj = typeof what == 'object'
		        ? what : document.getElementById(what);

		    if (obj.style.display == 'none')
		        obj.style.display = 'block';
		    else
		        obj.style.display = 'none';
		    return false;
		}
	//--></script>
</head>

<body class="mobile is-responsive  guest  iphone en-US new_header is-global-nav is-touch" data-clearable-enabled="true"
	onload="return hidePageElement('unevensplit')">



<h1>It's {{top_user['name']}}'s turn to pay!</h1>

<h2> Current Tab </h2>

<table class="current_tab">
	% for u in users:	
		<tr><td>{{u['name']}} {{'borrowed' if u['total_borrowed'] >= 0 else 'lent'}} ${{"%.0f" % abs(u['total_borrowed'])}}</td></td>
	% end
</table>

<h2> New Bill </h2>
	<form id="billInfo" method="post" action="newBill">

		<input type="hidden" name="group" value="{{group}}">
		<input type="hidden" name="response" value="html">
		<input placeholder="Date" type="date" name="billDate" value="{{today}}" /><br />
    	<select name="paid">
	    	  % for u in users:
				  <option value="{{u['user_id']}}" {{'selected="selected"' if u['user_id']==top_user['user_id'] else ''}}>{{u['name']}} paid</option>
			  % end
		</select><br />
		<input type="checkbox" id="split" name="evensplit" value="True" checked
			onchange="return (togglePageElementVisibility('evensplit') + togglePageElementVisibility('unevensplit'))">Split evenly {{len(users)}} ways<br />
<!--		<input type="radio" id="split" name="evensplit" value="False"
			onchange="return (togglePageElementVisibility('evensplit') + togglePageElementVisibility('unevensplit'))">Split unevenly<br /> -->
		<div id="evensplit">
			<input placeholder="Amount" type="number" name="amount" min="0" class="full-width"/><br />
		</div>
		<div id="unevensplit">
			<table>
			% for u in users:
			<tr>
				<td>{{u['name']}}'s share: </td>
				<td><input placeholder="Amount" type="number" name="amount-{{u['user_id']}}" min="0" class="half-width"/></td>
			<tr>
			% end
			</table>
		</div>
		<input placeholder="Notes" type="text" name="notes" class="full-width" /><br />
   		<button type="submit" form="billInfo" class="green">
              Split It!
        </button>
</form>


<table class="history_table">
	<tbody>
	<tr class="first_row">
		<th>Date</th>
		<th class="amount_header">Amount</th>
		<th>Paid By</th>
		<th>Notes</th>
	</tr>
	% for h in history:
	<tr>
		<td>{{h['bill_date']}}</td>
		<td class="amount">{{"%.2f" % h['bill_amount']}}</td>
		<td>{{h['paid_by'] + ('*' if not h['equal_split'] else '')}}</td>
		<td>{{h['notes']}}</td>
	</tr>
	% end
	</tbody>
</table>


<p class="history_table">
	{{'* Bill was split unequally' if sum([h['equal_split'] for h in history]) != len(history) else ''}}
</p>

<p>
<form id="changeGroup" method="get" action="/">
	<button type="submit" form="changeGroup" class="blue">
          Select a different group
    </button>
</form>
</p>

</body></html>