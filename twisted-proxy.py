# -*- coding: utf-8 -*-
__author__ = 'Vitalii Turovets'

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.enterprise import adbapi

from optparse import OptionParser
import ConfigParser
import os
import urlparse
import base64


class ConfigError(Exception):
    def __init__(self, message):
        self.message = message


class Config():
    def __init__(self):
            filename = "server.conf"
            self.possible_actions = ['add', 'modify', 'delete']
            self.required_action = None
            self.parser = OptionParser()
            self.parser.add_option("-f", dest="filename", help="proxy server configuration file (default: server.conf)")
            self.help_message = self.parser.format_help()
            options, args = self.parser.parse_args()
            options = options.__dict__
            if options['filename'] is not None:
                filename = options['filename']
            path = os.path.realpath(os.path.curdir)
            path = os.path.join(path, filename)
            if not os.path.isfile(path):
                raise ConfigError("Configfile %s not found!" % path)

            self.db_config = dict()
            parser_instance = ConfigParser.ConfigParser()
            parser_instance.read(filename)
            try:
                self.db_config = {
                    'host': parser_instance.get('database', 'host'),
                    'database': parser_instance.get('database', 'database'),
                    'username': parser_instance.get('database', 'username'),
                    'password': parser_instance.get('database', 'password')
                }
            except ConfigParser.NoSectionError, e:
                print "Database config section not found!"

            except ConfigParser.NoOptionError, e:
                print "Option %s in %s section not found." % e.option, e.section

    def __call__(self):
        return self.db_config

    def __getitem__(self, item):
        return self.db_config[item]


class MyProxyRequest(proxy.Request):

    ports = {'http': 80}
    protocols = {'http': proxy.ProxyClientFactory}

    def __init__(self, channel, queued, reactor=reactor):
        proxy.Request.__init__(self, channel, queued)
        self.reactor = reactor

    def process(self):
        auth_data = self.getHeader('proxy-authorization')
        if auth_data is None:
            self.setResponseCode(http.PROXY_AUTH_REQUIRED)
            self.finish()
        else:
            if 'Basic ' in auth_data:
                auth_data = auth_data.split(' ')
                auth_data_decoded = base64.b64decode(auth_data[1])
                username, password = auth_data_decoded.split(':')
                if not username or not password:
                    self.setResponseCode(http.INTERNAL_SERVER_ERROR)
                else:
                    deferred = self.search_for_user(username, password)
                    deferred.addCallback(self.authorize_user, username)
            else:
                self.setResponseCode(http.INTERNAL_SERVER_ERROR)

    def serve_request(self):
        parsed = urlparse.urlparse(self.uri)
        protocol = parsed[0]
        host = parsed[1]
        port = self.ports[protocol]
        rest = urlparse.urlunparse(('', '') + parsed[2:])
        if not rest:
            rest += '/'
        class_ = self.protocols[protocol]
        headers = self.getAllHeaders().copy()
        if 'host' not in headers:
            headers['host'] = host
        self.content.seek(0, 0)
        s = self.content.read()
        client_factory = class_(self.method, rest, self.clientproto, headers, s, self)
        self.reactor.connectTCP(host, port, client_factory)

    def authorize_user(self, query_results):
        if len(query_results) < 1:
            self.setResponseCode(http.UNAUTHORIZED)
            self.finish()
        else:
            self.serve_request()

    def search_for_user(self, username, password):
        query = "SELECT User FROM users WHERE User='%s' AND Password=PASSWORD('%s')" % (username, password)
        return db_pool.runQuery(query)


class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest


class ProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return MyProxy()


config = Config()

db_pool = adbapi.ConnectionPool("MySQLdb",
                                db=config['database'],
                                host=config['host'],
                                user=config['username'],
                                passwd=config['password'])
db_pool.connect()
db_pool.start()

reactor.listenTCP(3128, ProxyFactory())
reactor.run()