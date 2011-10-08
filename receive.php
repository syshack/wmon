<?php
include("config.php");

if (!isset($_POST['secret']) || $_POST['secret'] != SECRET)
{
    exit('403');
}

$server_name = isset($_POST['name']) ? trim($_POST['name']) : '';
$data        = trim($_POST['data']);

if (empty($server_name) || empty($data))
{
    exit('fail');
}

$data = explode(';', $data);

$wmon_log = array();
$wmon_log['server_name'] = $server_name;
$wmon_log['ip'] = $_SERVER['REMOTE_ADDR'];
foreach($data as $log)
{
    $log = explode(':', $log, 2);
    $wmon_log[$log[0]] = $log[0] == 'time' ? intval($log[1]) : trim($log[1]);
}

$log = array();
foreach($wmon_log as $name=>$value)
{
    $log[] = "`$name`='$value'";
}

$log = implode(',', $log);
$sql = "INSERT INTO wmon_log SET ".$log;

$link = mysql_connect(MYSQL_HOST.':'.MYSQL_PORT, MYSQL_USER, MYSQL_PASS);
if (!$link)
{
    die('Could not connect db: ' . mysql_error());
}

$db_selected = mysql_select_db(MYSQL_DB, $link);
if (!$db_selected) {
    die ('Can not select db:' . mysql_error());
}

mysql_query($sql, $link);
mysql_close($link);

echo "ok";

