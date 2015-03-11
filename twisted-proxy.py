# -*- coding: utf-8 -*-
__author__ = 'Vitalii Turovets'

from twisted.web import proxy, http
from twisted.internet import reactor

class ProxyFactory(http.HTTPFactory):
    def buildProtocol(self, addr):
        return proxy.Proxy()

reactor.listenTCP(3128, ProxyFactory())
reactor.run()