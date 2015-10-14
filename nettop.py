"""
Collect network traffic information similar to nettop. Borrows heavily from
Giampaolo Rodola's nettop simulator here:
# https://github.com/giampaolo/psutil/blob/master/examples/nettop.py
# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""

import time
import sys
import psutil
from MeteorClient import MeteorClient

# DDP python client based on the example here: 
# https://github.com/hharnisc/python-meteor/blob/master/example.py

client = MeteorClient('ws://127.0.0.1:3000/websocket')

# Meteor client callbacks
def subscribed(subscription):
    print('* SUBSCRIBED {}'.format(subscription))

def connected():
    print('* CONNECTED')

def subscription_callback(error):
    if error:
        print(error)

def insert_callback(error, data):
    if error:
        print(error)
        return
    #print(data)

client.on('subscribed', subscribed)
client.on('connected', connected)

# Nettop simulator
def poll():
    """Retrieve raw stats"""
    tot = psutil.net_io_counters()
    pnic = psutil.net_io_counters(pernic=True)
    return (tot, pnic)

def send_to_mongo(tot, pnic):
    # List of all interface names
    nic_names = list(pnic.keys())
    ifaces = len(nic_names)
    # all interfaces
    client.insert('networking', {
        'ifname': 'all',
        'num_ifaces': ifaces,  
        'bytes_sent': tot.bytes_sent, 
        'bytes_received': tot.bytes_recv,
        'packets_sent': tot.packets_sent,
        'packets_received': tot.packets_recv, 
        'timestamp': int(time.time())}, callback=insert_callback)

    for name in nic_names:
        # Traffic per interface
        client.insert('networking', {
            'ifname': name,
            'bytes_sent': pnic[name].bytes_sent, 
            'bytes_received': pnic[name].bytes_recv,
            'packets_sent': pnic[name].packets_sent,
            'packets_received': pnic[name].packets_recv, 
            'timestamp': int(time.time())}, callback=insert_callback)

def main():
    try:
        client.connect()
        client.subscribe('networking')
        print "Updating network data..."
        while True:
            args = poll()
            send_to_mongo(*args)
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        client.unsubscribe('networking')
        pass

if __name__ == '__main__':
    main()
