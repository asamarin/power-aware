#!/usr/bin/env python

import sys
import snmp
import xmlparser

class BladePower():
    """ Clase para la gestion de energia del IBM BladeCenter """
    
    # Power info dictionary indexes
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
            self.power_info = {}
            self.snmp_settings = {}
            self.oids = {}
            self.module_names = []
            self.xmlparser = xmlparser.XMLParser()

            if xmlsettings_file is not None:
                self.load_blade_settings(xmlsettings_file)
                self.blade_snmp = snmp.SNMP(**self.snmp_settings)
                self.module_names = self.get_module_names()
                power_domains = self.get_power_info()
                self.power_info[self.POWER] = dict(zip(self.module_names, power_domains))
                print "########"
                #print self.power_info
                sorted_modules = self.power_info[self.POWER].keys()
                sorted_modules.sort()
                for module in sorted_modules:
                    print module, ':', self.power_info[self.POWER][module]
                print "########"
                print "Consumo de verode04: ", self.power_info[self.POWER]["verode04"]

        except Exception as e:
            print >> sys.stderr, e

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
        print pd1modules
        print "[DEBUG] Getting power domain 2 modules..."
        pd2modules = self.blade_snmp.walk(self.oids[self.PD2_MODULES])
        print pd2modules
        return pd1modules + pd2modules

    def get_power_info(self):
        print "[DEBUG] Getting power domain 1 info..."
        powerdomain1 = self.blade_snmp.walk(self.oids[self.PD1_CURRPWR])
        print powerdomain1
        print "[DEBUG] Getting power domain 2 info..."
        powerdomain2 = self.blade_snmp.walk(self.oids[self.PD2_CURRPWR])
        print powerdomain2
        return powerdomain1 + powerdomain2


if __name__ == '__main__':
    bc = BladePower("./xml/bladecenter.xml")
