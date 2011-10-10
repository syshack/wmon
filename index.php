<?php
include("config.php");

$link = mysql_connect(MYSQL_HOST.':'.MYSQL_PORT, MYSQL_USER, MYSQL_PASS);
if (!$link)
{
    die('Could not connect db: ' . mysql_error());
}

$db_selected = mysql_select_db(MYSQL_DB, $link);
if (!$db_selected) {
    die ('Can not select db:' . mysql_error());
}

if(isset($_GET['cvs']))
{
    $server = isset($_GET['server']) ? trim($_GET['server']) : '';
    if(!empty($server))
    {
        $before_week = time() - 7*24*60*60;
        $sql = "SELECT * FROM wmon_log WHERE server_name='$server' AND time > $before_week ORDER BY time DESC";
        $result = mysql_query($sql);
        
        $lines = array();
        while ($row = mysql_fetch_assoc($result))
        {
            $service_status = 0;
            $i = 1;

            foreach(explode('|', $row['services']) as $s)
            {
                $s = explode(' ', $s);
                if($s[2] == 0) $service_status+=$i;
                $i = $i*2;
            }
            
            $lines[] = $row['time'].",".$row['load'].",'".$service_status."','".str_replace(' ', '+',$row['top'])."'";
        }

        header("Content-Type:text/plain");
        echo implode("\n", $lines); 
        mysql_free_result($result);
    }
    mysql_close($link);
    exit;
}

include('lib/Mustache.php');
$sql = "SELECT server_name, ip FROM wmon_log GROUP BY server_name ORDER BY time";

$result = mysql_query($sql);
        
$servers = array();
while ($row = mysql_fetch_assoc($result))
{
    $servers[] = $row['server_name'];
}
mysql_free_result($result);

$host_content = array();
foreach($servers as $server)
{
    $sql = "SELECT * FROM wmon_log WHERE server_name='$server' ORDER BY time DESC LIMIT 1";
    $result = mysql_query($sql);
    $last_log = mysql_fetch_assoc($result);
    mysql_free_result($result);
   
    $host = new Mustache;
    $host->hostname       = $last_log['server_name'];
    $host->localtime      = $last_log['localtime'];
    $host->ip             = $last_log['ip'];
    $host->cpu_model_name = $last_log['cpu'];
    $host->uptime         = $last_log['uptime'];
    $host->cvs            = "index.php?cvs&server=".$last_log['server_name'];

    $top = array();
    foreach(explode('|', $last_log['top']) as $t)
    {
        $t = explode(' ', $t);
        $top[] = array(
            'cpu'=>$t[0],
            'user'=>$t[1],
            'process'=>$t[2]
        );
    }

    $partitions = array();
    foreach(explode('|', $last_log['partitions']) as $p)
    {
        $p = explode(' ', $p);
        $partitions[] = array(
            'disk'=>$p[0],
            'mount'=>$p[1],
            'size'=>$p[2],
            'used'=>$p[3],
            'free'=>$p[4],
            'usage'=>$p[5]
        );
    }
    
    $services = array();
    foreach(explode('|', $last_log['services']) as $s)
    {
        $s = explode(' ', $s);
        $services[] = array(
            'name'=>$s[0],
            'service'=>$s[1],
            'stat'=>$s[2] == '1' ? 'up' : 'down',
            'status'=>$s[2] == '1' ? '运行中' : '已停止'
        );
    }
    
    $host->top = $top;
    $host->partitions = $partitions;    
    $host->services =$services;
    
    $host_content[] = $host->render(file_get_contents('templates/host.html'));
}

mysql_close($link);

$home = new Mustache;
$home->content = implode("\n", $host_content);
echo $home->render(file_get_contents('templates/home.html'));
