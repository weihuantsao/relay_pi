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

g_host              = '140.113.134.139'
g_port              = 3060
g_heartbeat_rate    = 5
g_verbose           = 0
g_conn_type         = 1
g_running           = True
g_timeOut           = 0
g_live              = True
g_socket            = None

raspi_relay_a_pin = 23
raspi_relay_b_pin = 24


def on_exit(sig, func=None):
    global g_running
    global g_socket
    global g_live
    global g_verbose

    if (g_verbose == 1):
        print 'exit handler triggered'
    
    if (g_running == 1):
        g_running = 0
        g_socket.shutdown(socket.SHUT_RDWR)
        time.sleep(1)
        g_socket.close()
        g_live = False

def set_exit_handler(func):
    signal.signal(signal.SIGTERM,func)


def socket_output_thread():
    global g_running
    global g_socket
    global g_heartbeat_rate

    while g_running:
        text = 'live\r\n' 
        g_socket.send(text)
        time.sleep(g_heartbeat_rate)

def socket_input_thread():
    global g_socket
    global g_running
    global g_verbose

    socket_read_buffer = ''
    
    os.system("gpio -g mode %d out" % (raspi_relay_a_pin))
    os.system("gpio -g mode %d out" % (raspi_relay_b_pin))

    send_cmd = ''

    while g_running:
        socket_read_buffer = g_socket.recv(100)
        if not g_running:
            exit()
        
        if g_verbose:
            print socket_read_buffer

        s = socket_read_buffer.split(',')
        if len(s) > 2:
            if s[0] == 'a':
                if s[1] == '1':
                    os.system("gpio -g write %d 0" % (raspi_relay_a_pin))
                    if g_verbose:
                        print "relay A enable"
                else:
                    os.system("gpio -g write %d 1" % (raspi_relay_a_pin))
                    if g_verbose:
                        print "relay A disable"
            elif s[0] == 'b':
                if s[1] == '1':
                    os.system("gpio -g write %d 0" % (raspi_relay_b_pin))
                    if g_verbose:
                        print "relay B enable"
                else :
                    os.system("gpio -g write %d 1" % (raspi_relay_b_pin))
                    if g_verbose:
                        print "relay B disable"

def init_pipe():
    try:
        thread.start_new(socket_output_thread, ())
        thread.start_new(socket_input_thread,())
    except:
        print "Could nor start pipe thread ...."
        exit()  

def init_socket():
    global g_socket
    global g_host
    global g_port
    global g_verbose
    global g_conn_type

    try: 
        if (g_conn_type == 1):
            g_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif (g_conn_type == 2):
            g_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except:
        print "Error, init socket "
        exit()

    try:
        if (g_verbose == 1):
            print g_host , ' ' , g_port
        
        g_socket.connect((g_host , g_port))
    except:
        print "Error, NO server listening"
        exit()

def usage():
    sys.stderr.write("""USAGE: %s [option]
    ctl - A simpler bridge script for control relay and heartbeat conection

    option:
    -p, --port=PORT:    port, a number, default: 3040
    -h, --host:         remote IP address
    -t, --type          TCP=1 / UDP=2
    -v, --verbose       show the debug messages
    -r, --rate 
    -H, --help )
""" % (sys.argv[0], ))

def main():
    global g_port
    global g_host
    global g_heartbeat_rate
    global g_verbose
    global g_live
    global g_conn_type

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                "p:h:t:vr:H",
                ["port", "host", "type", "verbose", "baudrate", "rate", "help"]
                )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o,a in opts:
        if o in ("-p", "--port" ):
            g_port = int(a)
        elif o in ("-h", "--host"):
            g_host = str(a)
        elif o in ("-t", "--type"):
            g_conn_type = int(a)
        elif o in ("-v", "--verbose"):
            g_verbose = int(1)
        elif o in ("-r", "--rate"):
            g_heartbeat_rate = int(a)
        elif o in ("-H", "--help"):
            usage()
            sys.exit()
    
    init_socket()
    init_pipe()
    
    set_exit_handler(on_exit)

    while g_live:
        a = 1

############## Start
main()
