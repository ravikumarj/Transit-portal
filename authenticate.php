<?php 
     
  // Strip any dangerous text out of the search
	$username = htmlspecialchars($_GET['username']);
	$password = htmlspecialchars($_GET['password']);
       // print $username;
	//print $password;
	$str="python /var/www/client_rpc.py -v ".$username.":".$password;
	//print $str;
	exec($str,$res);

	print $res[0];






  ?>
