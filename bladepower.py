#!/usr/bin/env python

import sys
import snmp
import xmlparser
import time

class BladePower():
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
        try:
            self.power_data = {}
            self.snmp_settings = {}
            self.oids = {}
            self.module_names = []
            self.xmlparser = xmlparser.XMLParser()

            if xmlsettings_file is not None:
                self.load_blade_settings(xmlsettings_file)
                self.blade_snmp = snmp.SNMP(**self.snmp_settings)
                #print "########"
                #print self.power_data
                print "Carga inicial de datos"
                self.module_names = self.get_module_names()
                self.update_power_data()
                sorted_modules = self.power_data[self.POWER].keys()
                sorted_modules.sort()
                for module in sorted_modules:
                    print module, ':', self.power_data[self.POWER][module]
                test_list = ["verode11", "verode12", "verode13", "verode14", "verode15"]
                self.test_run(test_list)
                #print "########"
                #print "Consumo de verode04: ", self.power_data[self.POWER]["verode04"]

        except Exception as e:
            print >> sys.stderr, e

    def update_power_data(self):
        power_domains = self.get_power_data()
        self.power_data[self.POWER] = dict(zip(self.module_names, power_domains))

    def test_run(self, *nodes):
        print "Ctrl-C para terminar"
        while(True):
            print "Refrescando datos de consumo..."
            ti = time.time()
            self.update_power_data()
            tf = time.time()
            if (tf - ti) < self.EPSILON:
                print "T = ", (tf - ti), " -> Peticion cacheada, descartada"
                continue
            for node in nodes:
                print "T = ", (tf - ti), " -> Peticion refrescada"
                print node, ':', self.power_data[self.POWER][node]

    def load_blade_settings(self, xmlsettings_file):
        self.xmlparser.parse_file(xmlsettings_file)
        root = self.xmlparser.get_root()
        parameters = [x.get("repr") for x in root.find("snmp")]
        values = [int(x.get("value")) if x.get("value").isdigit() else x.get("value") for x in root.find("snmp")]
        # Build up dictionary of SNMP session settings
        self.snmp_settings = dict(zip(parameters, values))

        # Now get all the OIDs defined
        oids_names = [x.get("descr") for x in root.find("oids")]
        oids_values = [x.get("value") for x in root.find("oids")]
        self.oids = dict(zip(oids_names, oids_values))

    def get_module_names(self):
        print "[DEBUG] Getting power domain 1 modules..."
        pd1modules = self.blade_snmp.walk(self.oids[self.PD1_MODULES])
        #print pd1modules
        print "[DEBUG] Getting power domain 2 modules..."
        pd2modules = self.blade_snmp.walk(self.oids[self.PD2_MODULES])
        #print pd2modules
        return pd1modules + pd2modules

    def get_power_data(self):
        print "[DEBUG] Getting power domain 1 data..."
        powerdomain1 = self.blade_snmp.walk(self.oids[self.PD1_CURRPWR])
        #print powerdomain1
        print "[DEBUG] Getting power domain 2 data..."
        powerdomain2 = self.blade_snmp.walk(self.oids[self.PD2_CURRPWR])
        #print powerdomain2
        return powerdomain1 + powerdomain2


if __name__ == '__main__':
    bc = BladePower("./xml/bladecenter.xml")
    
