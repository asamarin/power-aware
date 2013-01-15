#!/usr/bin/env python

import struct
import sys
import time
import cpu
import pi

MSR_RAPL_POWER_UNIT = 0x606

MSR_PKG_RAPL_POWER_LIMIT = 0x610
MSR_PKG_ENERGY_STATUS = 0x611
MSR_PKG_PERF_STATUS = 0x613
MSR_PKG_POWER_INFO = 0x614

MSR_PP0_POWER_LIMIT = 0x638
MSR_PP0_ENERGY_STATUS = 0x639
MSR_PP0_POLICY = 0x63A
MSR_PP0_PERF_STATUS = 0x63B

MSR_PP1_POWER_LIMIT = 0x640
MSR_PP1_ENERGY_STATUS = 0x641
MSR_PP1_POLICY = 0x642
                                  
MSR_DRAM_POWER_LIMIT = 0x618
MSR_DRAM_ENERGY_STATUS = 0x619
MSR_DRAM_PERF_STATUS = 0x61B
MSR_DRAM_POWER_INFO = 0x61C
                                  
POWER_UNIT_OFFSET = 0
POWER_UNIT_MASK = 0x0F
                                  
ENERGY_UNIT_OFFSET = 0x08
ENERGY_UNIT_MASK = 0x1F00
                                  
TIME_UNIT_OFFSET = 0x10
TIME_UNIT_MASK = 0xF000

def read_core_msr(core, offset):
    msr_filename = ("/dev/cpu/%d/msr") % core

    with open(msr_filename, 'rb') as f:
        f.seek(offset, 0)
        result = struct.unpack('@q', f.read(8))[0]   # Leer 8 bytes

    return result

def get_units(msr_rapl_power_unit):
    strings = ("power", "energy", "time")
    power_units = pow(0.5, float(msr_rapl_power_unit & 0xF))
    energy_units = pow(0.5, float((msr_rapl_power_unit >> 8) & 0x1F))
    time_units = pow(0.5, float((msr_rapl_power_unit >> 16) & 0xF))
    units = (power_units, energy_units, time_units)
    return dict(zip(strings, units))

def get_package_power_info(msr_pkg_power_info):
    strings = ("thermal_spec_power", "minimum_power", "maximum_power", "time_window")
    thermal_spec_power = pow(0.5, float(msr_pkg_power_info & 0x7FFF))
    minimum_power = pow(0.5, float((msr_pkg_power_info >> 16) & 0x7FFF))
    maximum_power = pow(0.5, float((msr_pkg_power_info >> 32) & 0x7FFF))
    time_window = pow(0.5, float((msr_pkg_power_info >> 48) & 0x7FFF))
    package = (thermal_spec_power, minimum_power, maximum_power, time_window)
    return dict(zip(strings, package))


if __name__ == '__main__':
    result = read_core_msr(0, MSR_RAPL_POWER_UNIT)
    units = get_units(result)
    print units
    result = read_core_msr(0, MSR_PKG_POWER_INFO)
    package = get_package_power_info(result)
    package['thermal_spec_power'] *= units['power']
    package['minimum_power'] *= units['power']
    package['maximum_power'] *= units['power']
    package['time_window'] *= units['time']
    #print package
    cpu0_before = read_core_msr(0, MSR_PKG_ENERGY_STATUS) * units['energy']
    cpu1_before = read_core_msr(1, MSR_PKG_ENERGY_STATUS) * units['energy']
    print "Package0 (cpu0) energy before:", cpu0_before, "J"
    print "Package1 (cpu1) energy before:", cpu1_before, "J"
    cores_before = [read_core_msr(x, MSR_PP0_ENERGY_STATUS) * units['energy'] for x in xrange(cpu.get_cpu_count())]
    for i in xrange(len(cores_before)):
        print "[*] Core", i, "energy before:", cores_before[i], "J"
    dram_before = read_core_msr(0, MSR_DRAM_ENERGY_STATUS) * units['energy']
    print "DRAM energy before:", dram_before, "J"

    #print "Sleeping 1 second..."
    #time.sleep(1)
    print "Calculating 30000 pi decimals..."
    pi.pi(30000)

    cpu0_after = read_core_msr(0, MSR_PKG_ENERGY_STATUS) * units['energy']
    cpu1_after = read_core_msr(1, MSR_PKG_ENERGY_STATUS) * units['energy']
    print "Package0 (cpu0) energy after:", cpu0_after, "J (", cpu0_after - cpu0_before, "J consumed)"
    print "Package1 (cpu1) energy after:", cpu1_after, "J (", cpu1_after - cpu1_before, "J consumed)"
    cores_after = [read_core_msr(x, MSR_PP0_ENERGY_STATUS) * units['energy'] for x in xrange(cpu.get_cpu_count())]
    for i in xrange(len(cores_after)):
        print "[*] Core", i, "energy after:", cores_after[i], "J (", cores_after[i] - cores_before[i], "J consumed)"
    dram_after = read_core_msr(0, MSR_DRAM_ENERGY_STATUS) * units['energy']
    print "DRAM energy after:", dram_after, "J (", dram_after - dram_before, "J consumed)"
