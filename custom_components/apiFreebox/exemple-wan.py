#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This example can be run safely as it won't change anything in your box configuration
'''


try: 
   from . import freepybox
except:
   import freepybox
# Instantiate Freepybox class using default application descriptor 
# and default token_file location
fbx = freepybox.freepybox()

# Connect to the freebox with default http protocol
# and default port 80
# Be ready to authorize the application on the Freebox if you use this
# example for the first time
fbx.open('mafreebox.freebox.fr', 80)

# Extract WAN interface status (GET /api/v6/connection/full) using connection API
fbx_connection_status_details = fbx.connection.get_status_details()
#print(fbx_connection_status_details)

print('### WAN ###')
print('WAN ipv4 address: {0}'.format(fbx_connection_status_details['ipv4']))
print('WAN ipv6 address: {0}'.format(fbx_connection_status_details['ipv6']))
print('WAN status: {0}'.format(fbx_connection_status_details['state']))

print('WAN down bandwidth: {0} Mb'.format(fbx_connection_status_details['bandwidth_down']/1000000))
print('WAN up bandwidth: {0}  Mb'.format(fbx_connection_status_details['bandwidth_up']/1000000))
print('WAN type: {0}'.format(fbx_connection_status_details['type']))
print('WAN media: {0}'.format(fbx_connection_status_details['media']))

# Extract xDSL interface stats  (GET /api/v6/connection/xdsl)
fbx_connection_xdsl_details = fbx.connection.get_xdsl_stats()
#print(fbx_connection_status_details)

print('\n')
print('### xDSL ###')
#print('xDSL down : {0}'.format(fbx_connection_xdsl_details['down']))
print('xDSL down maxrate: {0}'.format(fbx_connection_xdsl_details['down']['maxrate']))
print('xDSL down attn: {0} dB'.format(fbx_connection_xdsl_details['down']['attn_10']/10))
print('xDSL down snr: {0} dB'.format(fbx_connection_xdsl_details['down']['snr_10']/10))
print('xDSL down crc: {0}'.format(fbx_connection_xdsl_details['down']['crc']))
print('xDSL down fec: {0}'.format(fbx_connection_xdsl_details['down']['fec']))

#print('xDSL up : {0}'.format(fbx_connection_xdsl_details['up']))
print('xDSL up maxrate: {0}'.format(fbx_connection_xdsl_details['up']['maxrate']))
print('xDSL up attn: {0} dB'.format(fbx_connection_xdsl_details['up']['attn_10']/10))
print('xDSL up snr: {0} dB'.format(fbx_connection_xdsl_details['up']['snr_10']/10))
print('xDSL up crc: {0}'.format(fbx_connection_xdsl_details['up']['crc']))
print('xDSL up fec: {0}'.format(fbx_connection_xdsl_details['up']['fec']))

#print('xDSL status : {0}'.format(fbx_connection_xdsl_details['status']))
print('xDSL modulation : {0}'.format(fbx_connection_xdsl_details['status']['modulation']))
print('xDSL protocol : {0}'.format(fbx_connection_xdsl_details['status']['protocol']))
print('xDSL uptime : {0} h'.format(fbx_connection_xdsl_details['status']['uptime']/3600))


fbx_player_status_details = fbx.freeplayer.get_freeplayer_list()
print( fbx_player_status_details)
print('fbx player : '.format(fbx_player_status_details))
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import parse_qsl
import urllib
lstPlayer = fbx_player_status_details
for x in lstPlayer:
	print( x )
	print( x["id"] )
	fbx_player_1_status_details = fbx.freeplayer.get_freeplayer(x["id"])
	print( fbx_player_1_status_details)
	print('fbx player 1 : {0} '.format(fbx_player_1_status_details["power_state"]))
	
	quoiRegarde = fbx_player_1_status_details["foreground_app"]["cur_url"]
	url = quoiRegarde
	print(quoiRegarde)
# Close the freebox session
fbx.close()

