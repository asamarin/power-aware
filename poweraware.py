#!/usr/bin/env python

import sys
import os
import snmp
import xmlparser
import time
import threading

class PowerAware(threading.Thread):
    """ Clase para la gestion de energia del IBM BladeCenter """
    
    # Threshold value, in seconds, to distinguish fresh values from SNMP queries
    EPSILON = 2

    # Power data dictionary indexes
    POWER = "power"
    TEMPS = "temps"
    VOLTS = "volts"

    # Module names list indexes
    PWRDOM1 = 0
    PWRDOM2 = 1

    # "Friendly names" for several outstanding OIDs
    PD1_CURRPWR = "pd1ModuleAllocatedPowerCurrent"
    PD2_CURRPWR = "pd2ModuleAllocatedPowerCurrent"
    PD1_MODULES = "pd1ModuleName"
    PD2_MODULES = "pd2ModuleName"

    def __init__(self, xmlsettings_file=None):
        super(PowerAware, self).__init__()
        self._stop = threading.Event()

        self.power_data = {}
        self.snmp_settings = {}
        self.oids = {}
        self.module_names = []
        self.xmlparser = xmlparser.XMLParser()

        if xmlsettings_file is not None:
            self.load_snmp_settings(xmlsettings_file)
            self.blade_snmp = snmp.SNMP(**self.snmp_settings)

    def update_module_names(self):
        self.module_names = self.get_module_names()

    def update_power_data(self):
        self.power_data[self.POWER] = dict(zip(self.module_names, self.get_power_data()))

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def dump(self, nodes):
        #print "Ctrl-C para terminar"
        if not os.path.exists('./dumps'):
            os.mkdir('./dumps')
        t_refresh = 0
        while not self.stopped():
            #print "Refrescando datos de consumo..."
            ti = time.time()
            self.update_power_data()
            tf = time.time()
            t_query = (tf - ti)
            if t_query < self.EPSILON:
                #print "T = ", t_query, " -> Peticion cacheada, descartada"
                t_refresh += t_query
                continue
            #print "T =", t_query, "-> Peticion refrescada, tiempo total =", t_refresh + t_query
            for node in nodes:
                path = './dumps/' + node + '.txt'
                with open(path, 'a') as dumpfile:
                    dumpfile.write("%10.2f\t%4.2f\t%d\n" % (tf, t_refresh + t_query, int(self.power_data[self.POWER][node][:-1])))
            t_refresh = 0

    def load_snmp_settings(self, xmlsettings_file):
        self.xmlparser.parse_file(xmlsettings_file)
        root = self.xmlparser.get_root()
        parameters = [x.get("repr") for x in root.find("snmp")]
        values = [int(x.get("value")) if x.get("value").isdigit() else x.get("value") for x in root.find("snmp")]
        # Build up dictionary of SNMP session settings
        self.snmp_settings = dict(zip(parameters, values))

        # Now get all defined OIDs
        oids_names = [x.get("descr") for x in root.find("oids")]
        oids_values = [x.get("value") for x in root.find("oids")]
        self.oids = dict(zip(oids_names, oids_values))

    def get_module_names(self):
        #print "[DEBUG] Getting power domain 1 modules..."
        pd1modules = self.blade_snmp.walk(self.oids[self.PD1_MODULES])
        #print "[DEBUG] Getting power domain 2 modules..."
        pd2modules = self.blade_snmp.walk(self.oids[self.PD2_MODULES])
        return pd1modules + pd2modules

    def get_power_data(self):
        powerdomain1 = self.blade_snmp.walk(self.oids[self.PD1_CURRPWR])
        powerdomain2 = self.blade_snmp.walk(self.oids[self.PD2_CURRPWR])
        return powerdomain1 + powerdomain2

