#!/usr/bin/python
# Copyright (c) 2016, Nishanth Menon
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Inspired by: http://www.jeroenbaten.nl/cardio-oxygen-saturation-monitoring-home/

import sys, serial, time, os, getopt
import MySQLdb
import datetime

class masimo:

    ser = None
    cnx = None
    serial_string = None
    masimo_type = None

    spo2 = None
    bpm = None
    pi = None
    alarm = "000000"
    exc = "000000"
    exc1 = "000000"

    exc_sensor_no = False
    exc_sensor_defective = False
    exc_low_perfusion = False
    exc_pulse_search = False
    exc_interference = False
    exc_sensor_off = False
    exc_ambient_light = False
    exc_sensor_unrecognized = False
    exc_low_signal_iq = False
    exc_masimo_set = False

    parse = None

    p_inc = 0

    # Setup the dict
    def __init__(self, t="rad8s1",term=None):
        self.masimo_type = t
        self.ser = serial.Serial()
        self.ser.port=term
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        self.ser.parity = serial.PARITY_NONE #set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        self.ser.timeout = None          #block read
        self.ser.xonxoff = False     #disable software flow control
        self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2     #timeout for write
        self.parse = {
            'rad8s1' : self._parse_rad8_serial_1,
            'rad7cs1' : self._parse_rad7_color_serial_1,
            'radbs1' : self._parse_rad_7_blue_serial_1
        }

        try:
           self.ser.open()
        except Exception, e:
            print("error open serial port: " + str(e))
            sys.exit(1)

        # setting up database Connection
        try:
            self.cnx = MySQLdb.connect(host= "192.168.0.1",
                                        user="logmasimo",
                                        passwd="log@masimo-iXie3ahl",
                                        db="logmasimo")
        except MySQLdb.Error, e:
           print( "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
           sys.exit(2)
        self.cur = self.cnx.cursor()

        self.ser.flushInput()
        self.ser.flushOutput()
        # Capture  first line and throw it away..
        self.ser.readline()

    def __del__(self):
        if not self.cnx is None:
            self.cnx.close()
        if not self.ser is None:
            self.ser.close()

    def grab_data(self):
        self.serial_string = self.ser.readline().rstrip()

    def is_format_valid(self):
        # First verify that the strings are all proper in the right places..
        if self.v_spo2 != 'SPO2':
            raise Exception ('Data format error: SPO2 is: ' , self.v_spo2)

        if self.v_bpm != 'BPM':
            raise Exception ('Data format error: BPM is: ' , self.v_bpm)

        if self.v_pi != "PI":
            raise Exception ('Data format error: PI is: ' , self.v_pi)

        if self.v_alarm != "ALARM":
            raise Exception ('Data format error: ALARM is: ' , self.v_alarm)

        if self.v_exc != "EXC":
            raise Exception ('Data format error: EXC is: ' , self.v_exc)

        if self.v_exc1 != "EXC1":
            raise Exception ('Data format error: EXC1 is: ' , self.v_exc1)

    def is_info_valid(self):
        # Verify if the data is valid as well
        # - SPO2, BPM, ALARM, EXC, EXC1 should be int
        # - PI should be a float
        try:
            tmp = int(self.spo2)
            tmp = int(self.bpm)
            tmp1 = float(self.pi)
            tmp = int(self.alarm,16)
            tmp = int(self.exc,16)
            tmp = int(self.exc1,16),
        except Exception as err:
            raise Exception('Data contents invalid',
                            "SPO2=" + self.spo2 +
                            "BPM=" + self.bpm +
                            "PI=" + self.pi +
                            "ALARM=" + self.alarm +
                            "EXC=" + self.exc +
                            "EXC1=" + self.exc1)

    def is_data_valid(self):
        self.is_format_valid()
        self.is_info_valid()

    def parse_data(self):
        try:
            self.parse[self.masimo_type]()
        except Exception as err:
            raise Exception('Unsupported type?' , self.masimo_type + ': ' + str(err));
        try:
            self.is_data_valid()
        except Exception as err:
            print "Data invalid" + str(err)


    def _print_data(self):
        # Enable the following for printing purposes..
        self._parse_alarm()
        self._parse_exception()
        print "SPO2: " + self.spo2
        print "BPM: " + self.bpm
        print "PI: " + self.pi
        print "ALARM: " + self.alarm
        print "EXCEPTION: " + self.exc
        print "EXCEPTION1: " + self.exc1
	print "Exception Decode: "
        print "No Sensor: " + str(self.exc_sensor_no)
	print "Sensor Defective: " + str(self.exc_sensor_defective)
	print "Low Perfusion: " + str(self.exc_low_perfusion)
	print "Pulse Search: " + str(self.exc_pulse_search)
	print "Interference: " + str(self.exc_interference)
	print "Sensor OFF: " + str(self.exc_sensor_off)
	print "Ambient Light: " + str(self.exc_ambient_light)
	print "Sensor Unrecognized: " + str(self.exc_sensor_unrecognized)
	print "Low Signal IQ: " + str(self.exc_low_signal_iq)
	print "Masimo Set: " + str(self.exc_masimo_set)

    def store_data(self):
        #print self.serial_string

        # If we have no data to record, then why record?
        if "-" in self.spo2 or "-" in self.bpm:
            return
        try:
            self.cur.execute ("INSERT INTO data"
            "(spo2, bpm, pi, alarm, exc, exc1)"
            "VALUES(%d, %d, %f, %d, %d, %d)" %
	        (int(self.spo2), int(self.bpm), float(self.pi),
		int(self.alarm,16), int(self.exc,16), int(self.exc1,16)))
            self.cnx.commit()
	    # print "Data posted: " + self.cur._last_executed
            # self._print_data()
        except MySQLdb.Error, e:
            print( "ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
            print( "Last query was: "+ self.cur._last_executed )
            self._print_data()

        self.p_inc = self.p_inc + 1
        if self.p_inc is 10:
            print ("Data(SPO2= %s BPM= %s) Stored at: %s" %(self.spo2, self.bpm, datetime.datetime.now()))
            self.p_inc = 0

    def _parse_alarm(self):
        val = int(self.alarm, 16)
# SPO2: 097
# BPM: 064
# PI: 00.80
# ALARM: 000018
        return

    def _parse_exception(self):
# Source: http://www.ontvep.ca/pdf/Masimo-Rad-8-User-Manual.pdf
# Trend Data format
# The exceptions are displayed as a 3 digit, ASCII encoded, hexadecimal
# value. The binary bits of the hexadecimal value are encoded as follows:
# 000 = Normal operation; no exceptions
# 001 = No Sensor
# 002 = Defective Sensor
# 004 = Low Perfusion
# 008 = Pulse Search
# 010 = Interference
# 020 = Sensor Off
# 040 = Ambient Light
# 080 = Unrecognized Sensor
# 100 = reserved
# 200 = reserved
# 400 = Low Signal IQ
# 800 = Masimo SET. This flag means the algorithm is running in full
# SET mode. It requires a SET sensor and needs to acquire some
# clean data for this flag to be set
        val = int(self.exc, 16)
        self.exc_sensor_no = True if val & 1 else False
        self.exc_sensor_defective = True if val & 2 else False
        self.exc_low_perfusion = True if val & 4 else False
        self.exc_pulse_search = True if val & 8 else False
        self.exc_interference = True if val & (1 << 4) else False
        self.exc_sensor_off = True if val & (2 << 4) else False
        self.exc_ambient_light = True if val & (4 << 4) else False
        self.exc_sensor_unrecognized = True if val & (8 << 4) else False
        self.exc_low_signal_iq = True if val & (4 << 8) else False
        self.exc_masimo_set = True if val & (8 << 8) else False

    def _parse_rad8_serial_1(self):
	# 03/19/16 13:37:12 SN=0000093112 SPO2=---% BPM=---% DESAT=-- PIDELTA=+-- ALARM=0000 EXC=000001
        S = self.serial_string.replace('=', ' ')
        S = S.replace('%', ' ')
        ord = S.split(' ')

        self.v_spo2 = MySQLdb.escape_string(ord[4])
        self.v_bpm = MySQLdb.escape_string(ord[7])
        self.v_pi = MySQLdb.escape_string(ord[9])
        self.v_alarm = MySQLdb.escape_string(ord[22])
        self.v_exc = MySQLdb.escape_string(ord[24])
        self.v_exc1 = "EXC1"

        self.spo2 = MySQLdb.escape_string(ord[5])
        self.bpm = MySQLdb.escape_string(ord[8])
        self.pi = MySQLdb.escape_string(ord[10])
        self.alarm = MySQLdb.escape_string(ord[23])
        self.exc = MySQLdb.escape_string(ord[25])
        self.exc1 = MySQLdb.escape_string("00000000")

    def _parse_rad7_color_serial_1(self):
	# 03/17/16 19:19:36 SN=---------- SPO2=098% BPM=123 PI=00.55 SPCO=--% SPMET=--.-% SPHB=--.- SPOC=-- RESVD=--- DESAT=-- PIDELTA=+-- PVI=--- ALARM=000000 EXC=0000C00 EXC1=00000000
        S = self.serial_string.replace('=', ' ')
        S = S.replace('%', ' ')
        ord = S.split(' ')

        self.v_spo2 = MySQLdb.escape_string(ord[4])
        self.v_bpm = MySQLdb.escape_string(ord[7])
        self.v_pi = MySQLdb.escape_string(ord[9])
        self.v_alarm = MySQLdb.escape_string(ord[29])
        self.v_exc = MySQLdb.escape_string(ord[31])
        self.v_exc1 = MySQLdb.escape_string(ord[33])

        self.spo2 = MySQLdb.escape_string(ord[5])
        self.bpm = MySQLdb.escape_string(ord[8])
        self.pi = MySQLdb.escape_string(ord[10])
        # have to find this experimentally
        self.alarm = MySQLdb.escape_string(ord[30])
        self.exc = MySQLdb.escape_string(ord[32])
        # I dont seem to have data to decode this
        self.exc1 = MySQLdb.escape_string(ord[34])

    def _parse_rad_7_blue_serial_1(self):
	# http://www.infiniti.se/upload/Servicemanual/Masimo/SM_EN_RADICA7_Radical-7%20Service%20manual%20rev.A.pdf
	# 05/15/07 08:12:21 SN=0000070986 SPO2=---% BPM=--- PI=--.--% SPCO=--.-% SPMET=--.-% DESAT=-- PIDELTA=+-- PVI=--- ALARM=0000 EXC=000000 
        raise Exception('To be Implemented')



class main:
    supported_types=[ "rad8s1" , "rad7cs1", "rad7bs1" ]
    m = None
    t = None
    term = None

    def usage(self):
        print "-t type -d device"
        print self.supported_types

    def __init__(self):
        try:
            opts, args = getopt.getopt( sys.argv[1:],
                    "ht:d:",
                    ["help",  "type=", "device="])
        except getopt.GetoptError as err:
            print str(err)
            self.usage()
            sys.exit(err)

        self.t = "rad8s1"
        self.term = None

        for o, a in opts:
            if o in ('-h', "--help"):
                print "Help:"
                self.usage()
                sys.exit(0)
            elif o in ('-t', "--type"):
                self.t = a
            elif o in ('-d', "--device"):
                self.term = a
            else:
                print o
                assert False, "unhandled Option"

        if self.term is None:
            print "Need terminal device and type of masimo"
            self.usage()
            sys.exit(0)
        if not self.t in self.supported_types:
            print "need a valid supported type"
            self.usage()
            sys.exit(0)

        self.m = masimo(self.t, self.term)

    def main(self):
        print "Capturing data..:"
        while True:
            self.m.grab_data()
            # The following two steps may fail at times.. just move on..
            try:
                self.m.parse_data()
                self.m.store_data()
            except Exception as err:
                print "Exception noticed: " + str(err)


if __name__ == "__main__":
    m = main()
    m.main()
