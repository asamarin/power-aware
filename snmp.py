#!/usr/bin/env python

import netsnmp

class SNMP:
    """ Sesion SNMP sencilla """

    def __init__(self, 
                 Version=1, 
                 DestHost="localhost", 
                 Community="public", 
                 SecName="guest", 
                 Timeout=1000000):
        """ Parametros de sesion por defecto """

        self.version = Version
        self.desthost = DestHost
        self.username = SecName
        self.community = Community
        self.timeout = Timeout

    def walk(self, oid):
        """ Ejecuta el equivalente a un 'snmpwalk' con los parametros establecidos """

        try:
            result = netsnmp.snmpwalk(oid, Version=self.version, DestHost=self.desthost,
                                      SecName=self.username, Community=self.community, Timeout=self.timeout)
            return result
        except Exception as e:
            print type(e)

    def get(self, oid):
        """ Ejecuta el equivalente a un 'snmpget' con los parametros establecidos """

        try:
            result = netsnmp.snmpget(oid, Version=self.version, DestHost=self.desthost,
                                     SecName=self.username, Community=self.community, Timeout=self.timeout)
            return result
        except Exception as e:
            print type(e)

