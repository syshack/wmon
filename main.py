#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import datetime,time
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import pystache
from pystache import Loader
import config

class Server(db.Model):
    """docstring for Server"""
    server_name = db.StringProperty()
    cpu         = db.StringProperty()
    ip          = db.StringProperty()
    last_check  = db.DateTimeProperty()


class MonLog(db.Model):
    server_name = db.StringProperty()
    ip          = db.StringProperty()
    datetime    = db.DateTimeProperty(auto_now_add=True)
    time        = db.IntegerProperty()
    cpu         = db.StringProperty()
    uptime      = db.StringProperty()
    load        = db.StringProperty()
    top         = db.StringListProperty()
    partitions  = db.StringListProperty()
    services    = db.StringListProperty()

class BaseHandler(webapp.RequestHandler):
    """docstring for BaseHandler"""

    def write(self, content):
        """docstring for write"""

        self.response.out.write(content)

    def render(self, template_name, **kargs):

        self.write(self.render_string(template_name, **kargs))

    def render_string(self, template_name, **kargs):

        template = Loader().load_template(template_name, 
                            template_dirs = os.path.join(os.path.dirname(__file__), 'templates'), 
                            encoding='utf-8',
                            extension='html')
        
        return pystache.render(template, **kargs)

class MainHandler(BaseHandler):

    def get(self):

        servers = Server.all()

        log_items = []
        for server in servers:

            logs = MonLog.gql("WHERE server_name = :server_name ORDER BY time DESC limit 1", server_name=server.server_name)

            if not logs:
                continue

            log = logs[0]

            top = []
            for t in log.top:
                t = t.split(' ')
                top.append({
                    'cpu':t[0],
                    'user':t[1],
                    'process':t[2]
                })

            services = []
            for s in log.services:
                s = s.split(' ')
                services.append({
                    'name':s[0],
                    'service':s[1],
                    'stat': s[2] == '1' and 'up' or 'down',
                    'status': s[2] == '1' and u'运行' or u'停止'
                })

            partitions = []
            for p in log.partitions:
                p = p.split(' ')
                partitions.append({
                    'disk':p[0],
                    'mount':p[1],
                    'size':p[2],
                    'used':p[3],
                    'free':p[4],
                    'usage':p[5]
                })

            content = self.render_string("host",
                            hostname = log.server_name,
                            hostvar = log.server_name,
                            ip = log.ip,
                            cvs = "/log?server=%s" % log.server_name,
                            partitions = partitions,
                            cpu_model_name = log.cpu,
                            uptime = log.uptime,
                            services = services,
                            top = top
                        )

            log_items.append(content)

        if log_items:
            content = "\n".join(log_items)
        else:
            content = "<p style='text-align:center'>no data</p>"

        self.render('home', content=content)


class LogHandler(BaseHandler):

    def get(self):
        server_name = self.request.get("server").strip()
        logs = MonLog.gql("WHERE server_name = :server_name and time > :time ORDER BY time DESC limit 10000", server_name=server_name, time = int(round(time.time()-7*24*60*60)))

        log_lines = []

        for log in logs:

            service_status = 0;
            i = 1;
            for service in log.services:
                service = service.split(' ')
                if service[2] == '0':
                    service_status += i

                i = i*2;

            log_lines.append("%s,%s,'%s','%s'"   % (log.time, log.load, service_status, "|".join(log.top).replace(' ', '+')))

        self.write("\n".join(log_lines))

class ReceiveHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        data = self.request.get("data").strip()
        server_name = self.request.get("name").strip()
        api_secret  = self.request.get("secret").strip()

        logging.info('receive:%s' % data)

        if api_secret != config.API_SECRET:
            self.write("403")
        elif not data or not server_name:
            self.write('fail')
        else:

            logs = data.split(';')

            monlog = MonLog()
            monlog.server_name = server_name
            monlog.datetime    = datetime.datetime.now()

            services = []
            for log in logs:
                log = log.split(':', 1)

                if log[0] == 'time':
                    monlog.time = int(round(float(log[1])))
                elif log[0] == 'cpu':
                    monlog.cpu = log[1]
                elif log[0] == 'uptime':
                    monlog.uptime = log[1]
                elif log[0] == 'load':
                    monlog.load = log[1]
                elif log[0] == 'top':
                    monlog.top = log[1].split('|')
                elif log[0] == 'partitions':
                    monlog.partitions = log[1].split('|')
                else:
                    services.append("%s %s" % (log[0], log[1]))

            if services:
                monlog.services = services

            monlog.ip  = self.request.remote_addr
            monlog.put()

            server = Server.get_by_key_name(server_name)
            if not server:
                server = Server(key_name=server_name)
                server.server_name = server_name
                server.cpu = monlog.cpu
                server.ip  = self.request.remote_addr

            server.last_check = datetime.datetime.utcnow()
            server.put()

            self.write('ok')

class RemoveLogHandler(BaseHandler):

    def get(self):
        """docstring for get"""
        logs = MonLog.gql('WHERE time < :time', time=int(round(time.time()-30*24*60*60)))

        for log in logs:
            log.delete()

        self.write('ok')

def main():
    application = webapp.WSGIApplication([
                        ('/', MainHandler),
                        ('/log', LogHandler),
                        ('/remove_log', RemoveLogHandler),
                        ('/receive', ReceiveHandler),
                        ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
