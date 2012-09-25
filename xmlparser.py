#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import xml.parsers.expat as EP

class XMLParser():
    
    def __init__(self, filepath=None):
        if filepath is not None:
            self.parse_file(filepath)

    def parse_file(self, filepath):
        try:
            self.tree = ET.parse(filepath)
            self.root = self.tree.getroot()
        except IOError:
            print >> sys.stderr, '[I/O Error] No such file or directory'
        except EP.ExpatError as e:
            print >> sys.stderr, '[XML Error] ' \
                + EP.ErrorString(e.code) + ': line ' \
                + e.lineno + ', column ' + e.offset
        except:
            raise Exception('[Unknown error] Cannot parse \"' + filepath + '\"')

    def get_tree(self):
        return self.tree
    
    def get_root(self):
        return self.root

    
