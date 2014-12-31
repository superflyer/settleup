<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" xmlns:og="http://ogp.me/ns#" xmlns:fb="https://www.facebook.com/2008/fbml">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>SettleUp - Choose Your Group</title>

   	<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <link rel="stylesheet" href="/styles/base.css" type="text/css">
    
</head>

<body class="mobile is-responsive  guest  iphone en-US new_header is-global-nav is-touch" data-clearable-enabled="true">

<h1>Welcome to SettleUp!</h1>

<h2> Choose your group </h2>

	% for g in groups:
	<p><form id="group{{g}}" method="post" action="./chooseGroup">
		<input type="hidden" value={{g}} name="group">
		<button type="submit" form="group{{g}}" class="green">
              {{', '.join([u['name'] for u in groups[g]])}}
            </button></form></p>
    % end

	<p><form id="newgroup" method="get" action="/newGroup">
		<button type="submit" form="newgroup" class="green">
              Create a new group
            </button></p>


</form>


</body></html>