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

# Inspired by:
# http://www.jeroenbaten.nl/cardio-oxygen-saturation-monitoring-home/

import sys
import serial
import time
import os
import getopt
import MySQLdb
import datetime
# sudo pip install config
from config import Config
import pymysql


class datastore_dump(object):
    spo2 = None
    bpm = None
    pi = None
    alarm = "000000"
    exc = "000000"
    exc1 = "000000"
    v_spo2 = None
    v_bpm = None
    v_pi = None
    v_alarm = None
    v_exc = None
    v_exc1 = None

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
    exc_unknown = 0

    alm_mute_pressed = False
    alm_triggered = False
    alm_bpm_low = False
    alm_bpm_high = False
    alm_spo2_low = False
    alm_spo2_high = False
    alm_unknown = 0

    def _print_data(self):
        # Enable the following for printing purposes..
        print("DATA @ " + str(datetime.datetime.now()))
        print("\tSPO2: %s\tBPM: %s\tPI: %s" % (self.spo2,
                                               self.bpm, self.pi))
        print("\tALARM: %s\t EXC: %s\t EXC1: %s" % (self.alarm,
                                                    self.exc, self.exc1))
        if int(self.exc, 16) != 0:
            if (self.exc_unknown != 0):
                exc_unknown_p = "\t Unknown Exception Code: 0x%08x \n" % (
                    self.exc_unknown)
            else:
                exc_unknown_p = ""

            print("\tException Decode: %s%s%s%s%s%s%s%s%s%s%s" % (
                "No Sensor " if self.exc_sensor_no else "",
                "Sensor Defective " if self.exc_sensor_defective else "",
                "Low Perfusion " if self.exc_low_perfusion else "",
                "Pulse Search " if self.exc_pulse_search else "",
                "Interference " if self.exc_interference else "",
                "Sensor OFF " if self.exc_sensor_off else "",
                "Ambient Light " if self.exc_ambient_light else "",
                "Sensor Unrecognized " if self.exc_sensor_unrecognized else "",
                "Low Signal IQ " if self.exc_low_signal_iq else "",
                "Masimo Set " if self.exc_masimo_set else "",
                exc_unknown_p
            ))

        if int(self.alarm, 16) != 0:
            if (self.alm_unknown != 0):
                alm_unknown_p = "\t Unknown Alarm Code: 0x%08x \n" % (
                    self.alm_unknown)
            else:
                alm_unknown_p = ""
            print("\tAlarm Decode: %s%s%s%s%s%s%s" % (
                "MUTED " if self.alm_mute_pressed else "",
                "TRIGGER " if self.alm_triggered else "",
                "BPM Low " if self.alm_bpm_low else "",
                "BPM High " if self.alm_bpm_high else "",
                "SPO2 Low " if self.alm_spo2_low else "",
                "SPO2 High " if self.alm_spo2_high else "",
                alm_unknown_p
            ))

    def parse_config(self, f):
        return

    def initalize(self):
        return

    def connect(self):
        return

    def store_data(self):
        self._print_data()
        return


class datastore_mysql(datastore_dump):
    mysql_host = None
    mysql_usr = None
    mysql_psswd = None
    mysql_db = None
    mysql_table = None

    cnx = None
    cur = None

    def parse_config(self, f):
        self.mysql_host = f.mysql.host
        self.mysql_usr = f.mysql.user
        self.mysql_psswd = f.mysql.password
        self.mysql_db = f.mysql.db
        self.mysql_table = f.mysql.table_name

    def connect(self):
        # setting up database Connection
        try:
            self.cnx = MySQLdb.connect(self.mysql_host,
                                       self.mysql_usr,
                                       self.mysql_psswd,
                                       self.mysql_db)
            self.cur = self.cnx.cursor()
        except MySQLdb.Error as e:
            raise Exception('Data format error: MySQL error: ', e.args[1])

    def store_data(self):
        try:
            self.cur.execute(
                "INSERT INTO %s"
                "(spo2, bpm, pi, alarm, exc, exc1)"
                "VALUES(%d, %d, %f, %d, %d, %d)" %
                (self.mysql_table, int(
                    self.spo2), int(
                    self.bpm), float(
                    self.pi), int(
                    self.alarm, 16), int(
                        self.exc, 16), int(
                            self.exc1, 16)))
            self.cnx.commit()
            # print "Data posted: " + self.cur._last_executed
        except MySQLdb.Error as e:
            print("ERROR %d IN CONNECTION: %s" % (e.args[0], e.args[1]))
            print("Last query was: " + self.cur._last_executed)


class datastore_elastic(datastore_dump):
    elastic_host = None
    elastic_port = None
    elastic_usr = None
    elastic_idx = None
    elastic_table = None

    es = None
    cur = None

    def parse_config(self, f):
        self.elastic_host = f.elasticsearch.host
        self.elastic_port = f.elasticsearch.port
        self.elastic_idx = f.elasticsearch.index
        self.elastic_table = f.elasticsearch.table_name

    def initalize(self):
        # sudo pip install elasticsearch
        global Elasticsearch
        global strftime
        try:
            from elasticsearch import Elasticsearch as Elasticsearch
            from time import gmtime, strftime
        except Exception as err:
            raise Exception(
                'elastic search Failed: "pip install elasticsearch"?',
                str(err))

        return

    def connect(self):
        try:
            self.es = Elasticsearch([{'host': self.elastic_host,
                                      'port': self.elastic_port}])
        except Exception as err:
            raise Exception('Elasticsearch connect failed :', str(err))

    def store_data(self):

        l_time = time.localtime()
        e_id = strftime("%Y%m%d%H%M%S", l_time)
        e_time = strftime("%m-%d-%Y %H:%M:%S %Z", l_time)
        try:
            self.es.index(index=self.elastic_idx,
                          doc_type=self.elastic_table,
                          id=e_id,
                          body={
                              "time": str(e_time),
                              "SPO2": int(self.spo2),
                              "BPM": int(self.bpm),
                              "PI": float(self.pi),
                              "alarm": int(self.alarm, 16),
                              "EXC": int(self.exc, 16),
                              "EXC1": int(self.exc1, 16),
                              "exc_sensor_no": int(self.exc_sensor_no),
                              "exc_sensor_defective": int(self.exc_sensor_defective),
                              "exc_low_perfusion": int(self.exc_low_perfusion),
                              "exc_pulse_search": int(self.exc_pulse_search),
                              "exc_interference": int(self.exc_interference),
                              "exc_sensor_off": int(self.exc_sensor_off),
                              "exc_ambient_light": int(self.exc_ambient_light),
                              "exc_sensor_unrecognized": int(self.exc_sensor_unrecognized),
                              "exc_low_signal_iq": int(self.exc_low_signal_iq),
                              "exc_masimo_set": int(self.exc_masimo_set),
                              "exc_unknown": int(self.exc_unknown),
                              "alm_mute_pressed": int(self.alm_mute_pressed),
                              "alm_triggered": int(self.alm_triggered),
                              "alm_bpm_low": int(self.alm_bpm_low),
                              "alm_bpm_high": int(self.alm_bpm_high),
                              "alm_spo2_low": int(self.alm_spo2_low),
                              "alm_spo2_high": int(self.alm_spo2_high),
                              "alm_unknown": int(self.alm_unknown)
                          })
        except Exception as err:
            print('Elasticsearch data push failed :' + str(err))


class masimo:

    ser = None
    cnx = None
    serial_string = None
    masimo_type = None

    parse = None

    p_inc = 0

    store = None

    # Setup the dict
    def __init__(self, t="rad8s1", term=None,
                 store=None):
        self.masimo_type = t
        self.store = store

        self.ser = serial.Serial()
        self.ser.port = term
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self.ser.timeout = None  # block read
        self.ser.xonxoff = False  # disable software flow control
        self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2  # timeout for write

        self.parse = {
            'rad8s1': self._parse_rad8_serial_1,
            'rad7cs1': self._parse_rad7_color_serial_1,
            'radbs1': self._parse_rad_7_blue_serial_1
        }

        try:
            self.ser.open()
        except Exception as e:
            print("error open serial port: " + str(e))
            sys.exit(1)

        try:
            self.store.initalize()
            self.store.connect()
        except Exception as e:
            print("Eror init/open DB: " + str(e))
            sys.exit(2)

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
        if self.store.v_spo2 != 'SPO2':
            raise Exception('Data format error: SPO2 is: ', self.store.v_spo2)

        if self.store.v_bpm != 'BPM':
            raise Exception('Data format error: BPM is: ', self.store.v_bpm)

        if self.store.v_pi != "PI":
            raise Exception('Data format error: PI is: ', self.store.v_pi)

        if self.store.v_alarm != "ALARM":
            raise Exception(
                'Data format error: ALARM is: ',
                self.store.v_alarm)

        if self.store.v_exc != "EXC":
            raise Exception('Data format error: EXC is: ', self.store.v_exc)

        if self.store.v_exc1 != "EXC1":
            raise Exception('Data format error: EXC1 is: ', self.store.v_exc1)

    def is_info_valid(self):
        # Verify if the data is valid as well
        # - SPO2, BPM, ALARM, EXC, EXC1 should be int
        # - PI should be a float
        try:
            tmp = int(self.store.spo2)
            tmp = int(self.store.bpm)
            tmp1 = float(self.store.pi)
            tmp = int(self.store.alarm, 16)
            tmp = int(self.store.exc, 16)
            tmp = int(self.store.exc1, 16),
        except Exception as err:
            raise Exception('Data contents invalid',
                            "SPO2=" + self.store.spo2 +
                            "BPM=" + self.store.bpm +
                            "PI=" + self.store.pi +
                            "ALARM=" + self.store.alarm +
                            "EXC=" + self.store.exc +
                            "EXC1=" + self.store.exc1)

    def is_data_valid(self):
        self.is_format_valid()
        self.is_info_valid()

    def parse_data(self):
        try:
            self.parse[self.masimo_type]()
            self._parse_alarm()
            self._parse_exception()
        except Exception as err:
            raise Exception(
                'Unsupported type?',
                self.masimo_type + ': ' + str(err))
        try:
            self.is_data_valid()
        except Exception as err:
            print("Data invalid" + str(err))

    def store_data(self):
        # If we have no data to record, then why record?
        if "-" in self.store.spo2 or "-" in self.store.bpm:
            return
        self.store.store_data()
        self.p_inc = self.p_inc + 1
        if self.p_inc is 10:
            print("Data(SPO2= %s BPM= %s) Stored at: %s" %
                  (self.store.spo2, self.store.bpm, datetime.datetime.now()))
            self.p_inc = 0

    def _parse_alarm(self):
        val = int(self.store.alarm, 16)
        # SPO2: 097
        # BPM: 064
        # PI: 00.80
        # ALARM: 000018

        # DISCLAIMER:---- #3BEA9I support ticket number with Masimo
        # MASIMO Claims that the decode of ALARM bit fields is MASIMO Properitory information.
        # The following is the email from masimo:
        # "
        # Unfortunately that is prorietary information.
        # You will need to sign a non disclosure agreement and work with our legal department
        # to get that information.
        # "
        # Contact for Masimo USA: techservice-us@masimo.com
        # BUT I refused to sign NDA since that has two problems:
        # 1. I have to ask my current employer if I can indeed sign an NDA for something that
        #    is strictly my personal business and has no overlap that I know of with my employer
        #    and something that is being done on my own spare time
        # 2. I want ths resultant code - that is this very code to be BSD and opensource
        #    implying anyone can use it how ever they feel like.
        #
        # Hence, The following data
        # is based on MY PERSONAL DECODE based on experimentation with a RAD8 (the backup pulseox
        # at home). I will be unable to substantiate beyond the details of my experimentation
        # that I am documenting below - Please feel free to add to this decode with
        # additional data if you can decode any:

        # Test #1 -> with proper sensor data collected, press and release mute button:
        # we see 0x20 being set on ALARM and cleared -> (bit 5)
        self.store.alm_mute_pressed = True if val & (0x1 << 5) else False

        # Test #2
        # Based on data that everytime Alarm is audible and flashing, it is accompanied with
        # data 0x10 -> bit 4 set
        self.store.alm_triggered = True if val & (0x1 << 4) else False

        # Test #3
        # What happens when BPM goes out of range - Test Low
        # Test setup: connect to self, see BPM range, setup BPM off range a bit
        # my heart rate is 68, setup min bpm for 70, max to 185
        # I see 0x18 -> This should imply bit 3 is BPM lower than limit
        self.store.alm_bpm_low = True if val & (0x1 << 3) else False

        # Test #4
        # What happens when BPM goes out of range - Test High
        # Test setup: connect to self, see BPM range, setup BPM off range a bit
        # my heart rate is 68, setup min bpm for 45, max to 60
        # I see 0x14 -> This should imply bit 2 is BPM higher than limit
        self.store.alm_bpm_high = True if val & (0x1 << 2) else False

        # Test #5
        # What happens when O2 goes out of range - Test Low
        # Test setup: connect to self, see O2 range, setup O2 off range a bit
        # my SPO2 is 99%, setup min bpm for 98, max to none, then lightly
        # space sensor from finger to trigger low SPO2 alarm
        # I see 0x12 -> This should imply bit 1 is O2 lower than limit
        self.store.alm_spo2_low = True if val & (0x1 << 1) else False

        # Test #6
        # What happens when O2 goes out of range - Test High
        # Test setup: connect to self, see O2 range, setup O2 off range a bit
        # my SPO2 is 99%, setup min bpm for 85, max to 97
        # I see 0x11 -> This should imply bit 0 is O2 higher than limit
        self.store.alm_spo2_high = True if val & (0x1 << 0) else False

        # Alarm unknown - Save it for future analysis
        self.store.alm_unknown = val & ~((1 << 0) | (1 << 1) | (1 << 2) |
                                         (1 << 3) | (1 << 4) | (1 << 5))
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
        val = int(self.store.exc, 16)
        self.store.exc_sensor_no = True if val & 1 else False
        self.store.exc_sensor_defective = True if val & 2 else False
        self.store.exc_low_perfusion = True if val & 4 else False
        self.store.exc_pulse_search = True if val & 8 else False
        self.store.exc_interference = True if val & (1 << 4) else False
        self.store.exc_sensor_off = True if val & (2 << 4) else False
        self.store.exc_ambient_light = True if val & (4 << 4) else False
        self.store.exc_sensor_unrecognized = True if val & (8 << 4) else False
        self.store.exc_low_signal_iq = True if val & (4 << 8) else False
        self.store.exc_masimo_set = True if val & (8 << 8) else False
        # clear all known bits to find the unknown flags..
        self.store.exc_unknown = val & ~((1 << 0) | (1 << 1) | (1 << 2) |
                                         (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6) |
                                         (1 << 7) | (1 << 8) | (1 << 9) | (1 << 10) |
                                         (1 << 11))

    def _parse_rad8_serial_1(self):
        # 03/19/16 13:37:12 SN=0000093112 SPO2=---% BPM=---% DESAT=--
        # PIDELTA=+-- ALARM=0000 EXC=000001
        S1 = self.serial_string.decode(encoding='utf-8', errors='strict')
        S = S1.replace('=', ' ')
        S = S.replace('%', ' ')
        ord = S.split(' ')

        self.store.v_spo2 = pymysql.escape_string(ord[4])
        self.store.v_bpm = pymysql.escape_string(ord[7])
        self.store.v_pi = pymysql.escape_string(ord[9])
        self.store.v_alarm = pymysql.escape_string(ord[22])
        self.store.v_exc = pymysql.escape_string(ord[24])
        self.store.v_exc1 = "EXC1"

        self.store.spo2 = pymysql.escape_string(ord[5])
        self.store.bpm = pymysql.escape_string(ord[8])
        self.store.pi = pymysql.escape_string(ord[10])
        self.store.alarm = pymysql.escape_string(ord[23])
        self.store.exc = pymysql.escape_string(ord[25])
        self.store.exc1 = pymysql.escape_string("00000000")

    def _parse_rad7_color_serial_1(self):
        # 03/17/16 19:19:36 SN=---------- SPO2=098% BPM=123 PI=00.55 SPCO=--%
        # SPMET=--.-% SPHB=--.- SPOC=-- RESVD=--- DESAT=-- PIDELTA=+-- PVI=---
        # ALARM=000000 EXC=0000C00 EXC1=00000000
        S1 = self.serial_string.decode(encoding='utf-8', errors='strict')
        S = S1.replace('=', ' ')
        S = S.replace('%', ' ')
        ord = S.split(' ')

        self.store.v_spo2 = pymysql.escape_string(ord[4])
        self.store.v_bpm = pymysql.escape_string(ord[7])
        self.store.v_pi = pymysql.escape_string(ord[9])
        self.store.v_alarm = pymysql.escape_string(ord[29])
        self.store.v_exc = pymysql.escape_string(ord[31])
        self.store.v_exc1 = pymysql.escape_string(ord[33])

        self.store.spo2 = pymysql.escape_string(ord[5])
        self.store.bpm = pymysql.escape_string(ord[8])
        self.store.pi = pymysql.escape_string(ord[10])
        # have to find this experimentally
        self.store.alarm = pymysql.escape_string(ord[30])
        self.store.exc = pymysql.escape_string(ord[32])
        # I dont seem to have data to decode this
        self.store.exc1 = pymysql.escape_string(ord[34])

    def _parse_rad_7_blue_serial_1(self):
        # http://www.infiniti.se/upload/Servicemanual/Masimo/SM_EN_RADICA7_Radical-7%20Service%20manual%20rev.A.pdf
        # 05/15/07 08:12:21 SN=0000070986 SPO2=---% BPM=--- PI=--.--%
        # SPCO=--.-% SPMET=--.-% DESAT=-- PIDELTA=+-- PVI=--- ALARM=0000
        # EXC=000000
        raise Exception('To be Implemented')


class main:
    supported_types = ["rad8s1", "rad7cs1", "rad7bs1"]
    m = None
    t = None
    term = None
    f = None

    def usage(self):
        print("Usage:")
        print(sys.argv[0] + " -t type -d device -c config_file")
        print("Where:")
        print("\t-t: type of Masimo. One of: " + str(self.supported_types))
        print("\t-d: serial_port device like /dev/ttyUSB0")
        print("\t-c config_file (See config.cfg for example)")
        print("\t\t NOTE: -t and -d will override settings in config file")

    def import_config(self):
        # See https://www.red-dove.com/config-doc/
        try:
            db_type = self.f.db_type
        except Exception as err:
            raise Exception('Missing/Invalid params in config file for :' +
                            str(err),
                            "db_type should be one of 'mysql' 'dump' 'elasticsearch'")
        # Optional Properties
        try:
            self.term = self.f.serial_port
        except Exception as err:
            self.term = None
        try:
            self.t = self.f.masimo_type
        except Exception as err:
            self.t = "rad8s1"

        if db_type == "mysql":
            self.store = datastore_mysql()
        elif db_type == "elasticsearch":
            self.store = datastore_elastic()
        elif db_type == "dump":
            self.store = datastore_dump()
        else:
            print("Invalid type " + db_type + " assuming terminal print")
            # Default: assume terminal dump - but we should have
            # exception already..
            self.store = datastore_dump()

        # Data base specific parsing..
        try:
            self.store.parse_config(self.f)
        except Exception as err:
            raise Exception('Missing/Invalid params in config file for :',
                            str(err))

    def __init__(self):
        try:
            opts, args = getopt.getopt(
                sys.argv[
                    1:], "ht:d:c:", [
                    "help", "type=", "device=", "config_file="])
        except getopt.GetoptError as err:
            print(str(err))
            self.usage()
            sys.exit(err)

        self.t = "rad8s1"
        self.term = None

        for o, a in opts:
            if o in ('-h', "--help"):
                print("Help:")
                self.usage()
                sys.exit(0)
            elif o in ('-t', "--type"):
                self.t = a
            elif o in ('-d', "--device"):
                self.term = a
            elif o in ('-c', "--config_file"):
                try:
                    self.f = Config(a)
                except Exception as err:
                    raise Exception('Using Config file "' + a + '" Failed: ',
                                    str(err))
            else:
                print(o)
                assert False, "unhandled Option"

        if self.f is not None:
            self.import_config()
        else:
            raise Exception('Missing config file',
                            'Use "' + sys.argv[0] + ' -h" for help')

        if self.term is None:
            print("Need terminal device and type of masimo")
            self.usage()
            sys.exit(0)
        if self.t not in self.supported_types:
            print("need a valid supported type")
            self.usage()
            sys.exit(0)

        self.m = masimo(t=self.t,
                        term=self.term,
                        store=self.store)

    def main(self):
        print("Capturing data..:")
        while True:
            self.m.grab_data()
            # The following two steps may fail at times.. just move on..
            try:
                self.m.parse_data()
                self.m.store_data()
            except Exception as err:
                print("Exception noticed: " + str(err))


if __name__ == "__main__":
    m = main()
    m.main()
