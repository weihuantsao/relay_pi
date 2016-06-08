#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Create on 2014/01/21

@ Author:   Chris Ding
@ Version:  1.0
@ Email:    jiunting.d@gmail.com

'''

import getopt
import os
import signal
import time
import sys
import thread
import binascii
import socket

raspi_relay_a_pin = 23

os.system("gpio -g mode 23 out")

send_cmd = "gpio -g write " + str(raspi_relay_a_pin) +" 0"

os.system("gpio -g write %d 0" % (raspi_relay_a_pin))
