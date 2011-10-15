#简单服器监控

支持 gae 和 php 服务器， php可以运行于sae和任何支持php+mysql的服务器

#GAE安装

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

#SAE安装

1、修改 config.php 中的 API_SECRET 常量

2、按照gae安装 2-4步安装被监控服务器端

3、按照table.sql建mysql数据库表（在phpmyadmin里执行这段sql或用phpmyadmin导入）

4、参考sae文档使部署到sae,注：你可以将*.py加入svn跳过列表

#其它php服务器安装

1、按照sae安装 1-3步完成配置和被监控服务器安装

2、配置config.php中mysql配置

3、上传到服务器
