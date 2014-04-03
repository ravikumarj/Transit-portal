<?php 
     
    $username=$_GET['username'];
    $password=$_GET['password'];


  	$wisc=$_GET['WISC'];
  	$gatech=$_GET['GATECH'];
  	$prince=$_GET['PRINCE'];
  	$isi=$_GET['ISI'];
  	$uw=$_GET['UW'];
  	$amsix=$_GET['AMSIX'];
    $clemson=$_GET['CLEMSON'];

    $group=$_GET['group'];
    

$flag=0;
if($group == "Normal users")
  $str="python /var/www/client_rpc.py -a ";
else
  $str="python /var/www/client_rpc.py -r ";
if($wisc == "true")
{
  $str=$str."WISC";
  $flag=1;
}
if ($gatech == "true")
{
  if ($flag==0)
  {
    $str=$str."GATECH";
$flag=1;
  }
  else
    $str=$str.",GATECH";
}

if ($prince == "true")
{
if ($flag==0)
  {
  $str=$str."PRINCE";
  $flag=1;
}
else
  $str=$str.",PRINCE";
}

if($isi == "true")
{
  if ($flag==0)
  {
  $str=$str."ISI";
  $flag=1;
}
else
  $str=$str.",ISI";

}
if ($uw == "true")
{
  if ($flag==0)
  {
  $str=$str."UW";
  $flag=1;
  }
  else
    $str=$str.",UW";

}
if($amsix == "true")
{
  if ($flag==0)
  {
  $str=$str."AMSIX";
  $flag=1;
  }
else
  $str=$str.",AMSIX";
}
if($clemson == "true")
{
  if ($flag==0)
  {
  $str=$str."CLEMSON";
  $flag=1;
  }
else
  $str=$str.",CLEMSON";
}


$str=$str.":".$username;

exec($str,$res);


  print $res[0];

 

  ?>