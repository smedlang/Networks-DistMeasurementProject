#Savita Medlang
#EECS 325
#Project 2
#Measure number of hops to a destination
#Measure RTT time to send and receive a packet


import socket
import sys
import time
import string
import random
import select
import struct
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"
matplotlib.use('Agg')
import matplotlib.pyplot as plot
#import numpy as npy

# create a dummy socket to compare
# source: https://zeth.net/archive/2007/11/24/how-to-find-out-ip-address-in-python/
def local_data():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("case.edu", 80)) #one argument
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

port = 33434
ttl = 32 # value given

def set_up(hostname):
    timeout = struct.pack("ll",2,0)
    # get protocols for raw sockets
    ICMP_CODE = socket.getprotobyname('icmp')
    UDP_CODE = socket.getprotobyname('udp')

    # initialize send/recieve sockets
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP_CODE)
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)

    # message to identify packet
    msg = 'measurement for class project. questions to student sam290@case.edu or professor mxr136@case.edu'
    payload = ''.join(random.choice(string.ascii_uppercase) for i in range(1472)).encode('ascii')

    #set socket options
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
    
    #initialize timer
    SEND_TIME = time.time()
    
    # get ip of hostname to ping    
    try:
        host_ip = socket.gethostbyname(hostname)
    except:
        print( "Could not resolve hostname.")
        quit()

    recv_socket.bind(('', port))
	
	#udp probe
    send_socket.sendto(payload, (host_ip, port))
    

    # wait until data is available or timeout occurs
    ready = select.select([recv_socket], [], [], 2)
    if (ready):
        try:
		    # get data from recv_socket, pass to process_data
            recv_packet, _ = recv_socket.recvfrom(1024)
            RECV_TIME = time.time()
            process_data(recv_packet, hostname, host_ip, payload, SEND_TIME, RECV_TIME)
		
        except socket.error:
            print ("Unable to recieve packet %s." % (hostname))
            return
        finally:
            recv_socket.close()
            send_socket.close()
	

#method to unpack the ICMP packet and calculate hop nums and time
def process_data(recv_packet, hostname, host_ip, message, SEND_TIME, RECV_TIME):
    print("6")
    # ICMP response
	
    icmp_header = recv_packet[20:28]
    icmp_type, imcp_code, checksum, p_id, sequence = struct.unpack('bbHHh', icmp_header)
	
    # IPv4 header info
    unpacked_ip = struct.unpack('!BBHHHBBH4s4s', recv_packet[0:20])

    icmp_src = compile_string(recv_packet[12:16])
    icmp_dest = compile_string(recv_packet[16:20])

    # original IPv4 headers
    orig_ip_header = struct.unpack('!BBHHHBBH4s4s', recv_packet[28:48])
    resp_src_ip = compile_string(recv_packet[40:44])
    resp_dest_ip = compile_string(recv_packet[44:48])

    ttl_new = recv_packet[36]
    
    # source: http://www.networksorcery.com/enp/protocol/icmp/msg3.htm
    # if packet has not reached its final destination
    if(icmp_type != 3 and icmp_code != 3 or
        # if source ip is not the destination ip
        icmp_src != host_ip or
        # if destination ip does not match local data
        icmp_dest != local_data() or
        # if source ip of response does not match local data
        resp_src_ip != local_data() or
        # if destination ip of response is not the destination ip
        resp_dest_ip != host_ip or
        # if original message does not equal message in recv_packet
        len(recv_packet) == 59 and not (recv_packet[len(recv_packet)-4:]).decode("ascii") ==message):
        print ("Incorrect results for %s." % (hostname))
		
    # output
    hop_num = ttl - ttl_new
    print ("Data for %s, %s:" % (hostname, host_ip))
    print ("hops: %d" % (hop_num))
    RTT = (RECV_TIME - SEND_TIME) * 1000
    print ("RTT in ms: %f" % (RTT))
    print(("Number of bytes of original datagram = %s") % (bytes_of_orig_data(recv_packet[56:], message)))
    
    # plot hops and RTT
    plot.plot(hop_num, RTT, "bo", markersize = 6)
    print(str(hop_num) + " " + str(RTT))

# convert hostname to string ip
def compile_string(recv_packet):
    return str(recv_packet[0]) + "." + str(recv_packet[1]) + "." + str(recv_packet[2]) + "." + str(recv_packet[3])

# check if payloads are equal using minimum of message and recv_packet payload
def bytes_of_orig_data(recv_packet, message):
    sum = 0
    # minimum of message and recv_packet so you don't go our of bounds
    for i in range(min(len(message), len(recv_packet))):
        if(message[i] == recv_packet[i]):
            sum += 1
    return sum

# source: https://docs.python.org/2/tutorial/inputoutput.html
# open file in read mode
f = open('targets.txt', 'r')
for line in f:
    set_up(line.split()[0])
f.close()

 #source: http://matplotlib.org/1.3.1/examples/pylab_examples/line_styles.html
 #set up plot and export to output.png
plot.ylabel("RTT (ms)")
plot.xlabel("Hops")
plot.savefig('results.png')
input('Press ENTER to exit')
