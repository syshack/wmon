#简单服器监控(gae版)


#安装

1、配置 config.py 中的 API_SECRET

2、配置 pywmon.py:
    SERVER_NAME 服务名称，每台服务唯一
    API_SECRET 接口密码，必须和config.py中一样
    API_URL 你的gae地址
    SERVICES 要监按的服务，key服务名 value为服务运行的进程名字

3、上传pywmon.py到需要监控的服务，可以是多个服务器，不同 SERVER_NAME 即可

4、使用 cron 定时执行 pywmon.py 如 `*/5 * * * * /path/to/python /path/to/pywmon.py &> /dev/null`

5、修改app.yaml中 application id，使用gae sdk上传到的你的gae

6、完成，可以访问你的gae地址查看监控了
