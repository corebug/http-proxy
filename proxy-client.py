# -*- coding: utf-8 -*-
__author__ = 'Vitalii Turovets'


from optparse import OptionParser
import urllib2
from BaseHTTPServer import BaseHTTPRequestHandler


class ParseError(Exception):
        def __init__(self, message):
            self.message = message


class Config():
    def __init__(self):
        self.options = dict()
        self.parser = OptionParser()
        self.parser.set_usage("Usage: python proxy-client.py [OPTIONS] [URL]")
        self.parser.add_option("-U", dest="username", help="username for proxy auth")
        self.parser.add_option("-P", dest="password", help="password for proxy auth")
        self.parser.add_option("-s", dest="server", help="host with proxy, localhost by default")
        self.parser.add_option("-p", dest="port", help="proxy port, 3128 by default")

        self.help_message = self.parser.format_help()
        options, url = self.parser.parse_args()
        options = options.__dict__

        if not options['username']:
            raise ParseError('Username required!')
        if not options['password']:
            raise ParseError('Password required!')
        if not url:
            raise ParseError('URL required!')

        self.options['username'] = options['username']
        self.options['password'] = options['password']
        self.options['server'] = options['server'] or '127.0.0.1'
        self.options['port'] = options['port'] or '3128'

        self.options['proxy_url'] = "http://%s:%s@%s:%d" % (
            self.options['username'],
            self.options['password'],
            self.options['server'],
            int(self.options['port'])
        )
        self.options['url'] = url[0]

    def help(self):
        return self.help_message

    def __getitem__(self, item):
        if self.options:
            return self.options[item]

    def __call__(self):
        return self.options


class ProxyClient():
    def __init__(self, options):
        self.options = options

    def __call__(self, url):
        proxy_support_handler = urllib2.ProxyHandler({'http': self.options['proxy_url']})
        opener = urllib2.build_opener(proxy_support_handler)
        urllib2.install_opener(opener)
        fh = urllib2.urlopen(url)
        return fh.read().strip()

if __name__ == '__main__':
    try:
        config = Config()

        client = ProxyClient(config())

        print client(config['url'])

    except ParseError as value:
        print "Not enough parameters, use -h flag to see help."

    except AssertionError as value:
        print "Proxy error occured: %s" % value.message

    except urllib2.HTTPError, e:
        print "HTTP Error: %s, %s" % (str(e.code), BaseHTTPRequestHandler.responses[e.code])

    except urllib2.URLError, e:
        print "URL is incorrect, error: %s" % e.reason
