# -*- coding: utf-8 -*-
"""Keithley.py: A pyVISA wrapper for Keithley devices

__author__ = "Jason M. Battle"
__copyright__ = "Copyright 2016, Jason M. Battle"
__license__ = "MIT"
__email__ = "jason.battle@gmail.com"
"""

import visa

class M2308():
    
    def __init__(self, address=16):
        self._instr = visa.ResourceManager().open_resource('GPIB0::%s' % address) # Default GPIB address is 16
        self._result = 0
        self.reset()

    def reset(self):
        self._instr.write('*RST') # Reset to power-on defaults
        self._instr.write('DISPlay:TEXT:STATe 0') # LCD display must be separately reset

    def vset(self, vset):
        self._instr.write('SOURce1:VOLTage %.3f' % vset) # 1mV resolution, 0 ~ 15V range
        
    def ilim(self, ilim):
        self._instr.write('SOURce1:CURRent:LIMit:VALue %.4f' % ilim) # 100uV resolution, 6mA ~ 5A range 
        
    def vlim(self, vlim):
        self._instr.write('SOURce1:VOLTage:PROTection %i' % vlim) # 1V resolution, 0 ~ 8V range
        self._instr.write('SOURce1:VOLTage:PROTection:CLAMp 0') # Enable clamp
    
    def enable(self):
        self._instr.write('OUTPut1:STATe 1') # Enable Ch1 output
        
    def disable(self):
        self._instr.write('OUTPut1:STATe 0') # Disable Ch1 output
        
    def vmeas(self, smp_avgcount=5, smp_nplc=0.5, noise_floor=1e-3):
        if smp_avgcount < 0: # 1 ~ 10 sample averaging range 
            smp_avgcount = 1
        elif smp_avgcount > 10:
            smp_avgcount = 10
        if smp_nplc < 0.002: # 0.002 ~ 10 NPLC sampling (33 us ~ 167 ms) 
            smp_nplc = 0.002
        elif smp_nplc > 10:
            smp_nplc = 10
        self._instr.write('SENSe:FUNCtion "VOLTage"') # Set voltage sensing mode 
        self._instr.write('SENSe:AVERage %s' % smp_avgcount) # Set sample averaging
        self._instr.write('SENSe:NPLCycles %s' % smp_nplc) # Set sampling frequency
        self._result = round(float(self._instr.query('READ?').strip('\n')), 3) # Read and format response
        if self._result < noise_floor: # Zero sub mV values
            self._result = float(0)
        return self._result 
        
    def imeas(self, smp_avgcount=5, smp_nplc=0.5, noise_floor=100e-6):
        if smp_avgcount < 1: # 1 ~ 10 sample averaging range
            smp_avgcount = 1
        elif smp_avgcount > 10:
            smp_avgcount = 10
        if smp_nplc < 0.002: # 0.002 ~ 10 NPLC sampling (33 us ~ 167 ms)
            smp_nplc = 0.002
        elif smp_nplc > 10:
            smp_nplc = 10
        self._instr.write('SENSe:FUNCtion "CURRent"') # Set current sensing mode
        self._instr.write('SENSe:AVERage %s' % smp_avgcount) # Set sample averaging
        self._instr.write('SENSe:NPLCycles %s' % smp_nplc) # Set sampling frequency
        self._instr.write('SENSe:CURRent:RANGe:AUTO 1') # Enable auto range-finding
        self._result = round(float(self._instr.query('READ?').strip('\n')), 4) # Read and format response
        if (self._result < noise_floor) and (self._result > -noise_floor): # Zero sub 100uA values
            self._result = float(0)
        return self._result          
        
    def msgon(self, msg='TEST IN PROGRESS!!!!!!!!!!!!!!!!'):
        try:
            msg.isalnum() # Check for proper string entry
        except: 
            print 'Input message is not a string. Please try again.'
        else:
            self._instr.write('DISPlay:TEXT:DATA "%s"' % msg) # Write string
            self._instr.write('DISPlay:TEXT:STATe 1') # Enable text display mode
        
    def msgoff(self, msg=' '*32):
        self._instr.write('DISPlay:TEXT:DATA "%s"' % msg) # Restore default text
        self._instr.write('DISPlay:TEXT:STATe 0') # Disable text display mode
        
    def dispon(self):
        self._instr.write('DISPlay:ENABle 1') # Enable LCD
        
    def dispoff(self):
        self._instr.write('DISPlay:ENABle 0') # Disable LCD