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
#   Simple ICMP6 ping.
#
#   This implementation of ping uses the ICMP echo and echo-reply packets
#   to check the status of a host. If the remote host is up, it should reply
#   to the echo probe with an echo-reply packet.
#   Note that this isn't a definite test, as in the case the remote host is up
#   but refuses to reply the probes.
#   Also note that the user must have special access to be able to open a raw
#   socket, which this program requires.
#
# Authors:
#   Alberto Solino (@agsolino)
#
# Reference for:
#   ImpactPacket: ICMP6
#   ImpactDecoder
#

# Imports
import argparse
import select
import socket
import time

from impacket import ImpactDecoder, IP6, ICMP6, version


def main(argv=None):
    parser = argparse.ArgumentParser(description='Send ICMPv6 echo requests using a raw socket.')
    parser.add_argument('src', help='source IPv6 address')
    parser.add_argument('dst', help='destination IPv6 address')
    options = parser.parse_args(argv)

    print(version.BANNER)

    # Create a new IP packet and set its source and destination addresses.
    ip = IP6.IP6()
    ip.set_ip_src(options.src)
    ip.set_ip_dst(options.dst)
    ip.set_traffic_class(0)
    ip.set_flow_label(0)
    ip.set_hop_limit(64)

    # Open a raw socket. Special permissions are usually required.
    raw_socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)

    payload = b"A" * 156

    print("PING %s %d data bytes" % (options.dst, len(payload)))
    seq_id = 0
    while True:
        # Give the ICMP packet the next ID in the sequence.
        seq_id += 1
        icmp = ICMP6.ICMP6.Echo_Request(1, seq_id, payload)

        # Have the IP packet contain the ICMP packet (along with its payload).
        ip.contains(icmp)
        ip.set_next_header(ip.child().get_ip_protocol_number())
        ip.set_payload_length(ip.child().get_size())
        icmp.calculate_checksum()

        # Send it to the target host.
        raw_socket.sendto(icmp.get_packet(), (options.dst, 0))

        # Wait for incoming replies.
        if raw_socket in select.select([raw_socket], [], [], 1)[0]:
            reply = raw_socket.recvfrom(2000)[0]

            # Use ImpactDecoder to reconstruct the packet hierarchy.
            rip = ImpactDecoder.ICMP6Decoder().decode(reply)

            # If the packet matches, report it to the user.
            if ICMP6.ICMP6.ECHO_REPLY == rip.get_type():
                print("%d bytes from %s: icmp_seq=%d "
                      % (rip.child().get_size() - 4, options.dst, rip.get_echo_sequence_number()))

            time.sleep(1)


if __name__ == '__main__':
    main()
