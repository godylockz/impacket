#!/usr/bin/env python3
# -- coding: utf-8 --
# Impacket - Collection of Python classes for working with network protocols.
#
# Copyright Fortra, LLC and its affiliated companies 
#
# All rights reserved.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Description:
#   Simple packet sniffer.
#
#   This packet sniffer uses a raw socket to listen for packets
#   in transit corresponding to the specified protocols.
#
#   Note that the user might need special permissions to be able to use
#   raw sockets.
#
# Authors:
#   Gerardo Richarte (@gerasdf)
#   Javier Kohen
#
# Reference for:
#   ImpactDecoder
#

# Imports
import argparse
from select import select
import socket

from impacket import ImpactDecoder

DEFAULT_PROTOCOLS = ('icmp', 'tcp', 'udp')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Listen for IP packets using raw sockets.')
    parser.add_argument('protocol', nargs='*', help='protocol name, such as icmp, tcp, or udp')
    options = parser.parse_args(argv)

    if options.protocol:
        requested_protocols = options.protocol
    else:
        requested_protocols = list(DEFAULT_PROTOCOLS)
        print("Using default set of protocols. A list of protocols can be supplied from the command line.")

    # Open one socket for each specified protocol.
    # A special option is set on the socket so that IP headers are included with
    # the returned data.
    sockets = []
    active_protocols = []
    for protocol in requested_protocols:
        try:
            protocol_num = socket.getprotobyname(protocol)
        except socket.error:
            print("Ignoring unknown protocol:", protocol)
            continue
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol_num)
        raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sockets.append(raw_socket)
        active_protocols.append(protocol)

    if not sockets:
        print("There are no protocols available.")
        return

    print("Listening on protocols:", active_protocols)

    # Instantiate an IP packets decoder.
    # As all the packets include their IP header, that decoder only is enough.
    decoder = ImpactDecoder.IPDecoder()

    while sockets:
        # Wait for an incoming packet on any socket.
        ready = select(sockets, [], [])[0]
        for raw_socket in ready:
            packet = raw_socket.recvfrom(4096)[0]
            if not packet:
                # Socket remotely closed. Discard it.
                sockets.remove(raw_socket)
                raw_socket.close()
            else:
                # Packet received. Decode and display it.
                packet = decoder.decode(packet)
                print(packet)


if __name__ == '__main__':
    main()
