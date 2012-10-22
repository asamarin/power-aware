#!/usr/bin/env python

import poweraware as pa

if __name__ == '__main__':
    try:
        bcenter = pa.PowerAware("./xml/bladecenter.xml")
        print "Getting nodes..."
        bcenter.update_module_names()
        test_list = ["verode11", "verode12", "verode13", "verode14", "verode15"]
        bcenter.dump(test_list)
    except KeyboardInterrupt:
        print "Exiting SNMP agent..."
        bcenter.stop()
        bcenter.join()
    finally:
        print "Done"
