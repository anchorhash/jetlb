"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import argparse

# parse trace?
from scapy.layers.inet import IP, TCP
from scapy.utils import PcapReader


def extract_packet_key(pkt):
    if IP in pkt:
        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst

        if TCP in pkt:
            tcp_sport = pkt[TCP].sport
            tcp_dport = pkt[TCP].dport

            flow_id = str(ip_src) + '.' + str(tcp_sport) + '.' + str(ip_dst) + '.' + str(tcp_dport)

            ### print(" IP src " + str(ip_src) + " TCP sport " + str(tcp_sport))
            ### print(" IP dst " + str(ip_dst) + " TCP dport " + str(tcp_dport))

            return flow_id

    return None


def parse_trace(path, file_name):
    packet_reader = PcapReader(path)
    file = open(fn + ".bin", "ab")
    
    packet_number = 0
    
    while True:
        
        pkt = packet_reader.read_packet()
        if pkt is None:
            break

        flow_id = extract_packet_key(pkt)
        
        if flow_id:
            splitted_flow_id = flow_id.split(".")
            binary_flow_id = []
            
            for c in splitted_flow_id:
                if int(c) < 256:
                    binary_flow_id.append(int(c))
                else:
                    binary_flow_id.append(int(int(c)/256))
                    binary_flow_id.append(int(int(c)%256))
            
            binary_flow_id += [0] * (13 - len(binary_flow_id))
            
            file.write(bytearray(binary_flow_id))

        packet_number += 1
        if packet_number % 100000 == 0:
            print("parsed {} packets".format(packet_number))
        
    file.close()

    return


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description="create a binary that contains a sequence of 13 bytes 5-tuples from a pcap "
                    "file -- ignores non TCP packets",
        formatter_class=argparse.RawTextHelpFormatter)

    # path
    parser.add_argument('--path', '-p', default=10, type=int, help='path to pcap')

    ### file name
    parser.add_argument('--file_name', '-fn', default=10**8, type=int, help='file name')

    args = parser.parse_args()
    parse_trace(args.path, args.file_name)
