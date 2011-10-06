#!/usr/bin/env python
# -*- coding:utf-8 -*-

""""
INSTALL:
*/5 * * * * /path/to/python /path/to/pywmon.py &> /dev/null
"""

import os
import re
import urllib2, urllib
import time

SERVER_NAME = 'test'
API_SECRET  = 'secret'
API_URL     = 'http://your-id.appspot.com'
SERVICES    = {
        'mongodb':'mongod',
        'mysql':'mysqld',
        'apache':'apache2',
        'nginx':'nginx',
        'memcache':'memcached'
    }

class wmon(object):
    """docstring for wmon"""

    server_name = ""
    
    api_url    = ""
    api_secret = ""

    partitions_exclude = '^Filesystem|tmpfs|cdrom|mnt|none|//'

    services = {}

    def __init__(self):
        self.server_name = SERVER_NAME
        self.api_url     = API_URL
        self.api_secret  = API_SECRET
        self.services    = SERVICES

    def checkall(self):
        """docstring for checkall"""

        data = []
        data.append('time:%s' % time.time())
        data.append('cpu:%s' % self.cpu_model_name())
        data.append('uptime:%s' % self.uptime())
        data.append('top:%s' % self.top())
        data.append('load:%s' % self.load())
        data.append('partitions:%s' % "|".join(self.partitions()))
        
        for s in self.services:
            data.append('%s:%s' % (s, self.check_service(self.services[s])))

        data = ";".join(data)
        data = re.sub(r'[ ]+', ' ', data)
        
        return self.send(data)
        
    def send(self, data):

        req = urllib2.Request("%s/receive" % self.api_url)
        r = urllib2.urlopen(req, urllib.urlencode({'data':data, 'secret':self.api_secret, 'name':self.server_name}))
        res = r.read()
        r.close()
        return res
        
    def check_service(self, service):
        """docstring for check_serveice"""
        result = os.popen('ps ax -o \'%%c %%P\' | awk \'{if (($2 == 1) && ($1 == "\'%s\'")) print $0}\'' % service).read().strip("\n")
        result = re.sub(r'[ ]+', ' ', result)

        if result:
            return result
        else:
            return "%s 0" % service

    def cpu_model_name(self):
        """docstring for cpu_model_name"""

        cpuinfo = os.popen('cat /proc/cpuinfo').read()
        for line in cpuinfo.split('\n'):
            tmp = line.split(':', 1)
            if tmp[0].strip() == 'model name':
                return tmp[1].strip()
                
        return ""
    
    def uptime(self):
        """docstring for uptime"""
        return os.popen('uptime').read().strip("\n")

    def partitions(self):
        """docstring for partitions"""

        return os.popen('df -h | grep -vE \'%s\' | awk \'{ print $1 " " $6 " " $2 " " $3 " " $4 " " $5  }\'' % self.partitions_exclude).read().strip("\n").split("\n")

    def top(self):
        """docstring for top"""
        result = os.popen('ps axeo "%C %U %c" --sort -pcpu | head -n 7 | tail -n 6').read().replace('\n', '|').strip("|").replace('| ', '|').replace(' |', '|')
        result = re.sub(r'[|]+', '|', result)
        result = re.sub(r'[ ]+', ' ', result)

        return result.strip()

    def load(self):
        """docstring for load"""
        return os.popen("cat /proc/loadavg | cut -d' ' -f1,2,3 --output-delimiter=','").read().strip("\n")

if __name__ == '__main__':
    print wmon().checkall()
