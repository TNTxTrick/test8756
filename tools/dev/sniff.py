"""Sniff the packets that are passing through the host."""

from sys import argv
from scapy.all import sniff

def start_sniff(filter: str = "tcp", count: int = 50) -> None:
    """
    Start sniffing packets with specified filter and count.

    Args:
        filter (str): The BPF filter to apply for packet capture. Default is "tcp".
        count (int): The number of packets to capture. Default is 50.

    Returns:
        None
    """
    try:
        print(f"Starting packet sniffing with filter '{filter}' and count {count}...")
        capture = sniff(filter=filter, count=count)
        print("Packet capture summary:")
        capture.summary()
    except Exception as e:
        print(f"An error occurred while sniffing packets: {e}")

if __name__ == "__main__":
    try:
        if len(argv) > 2:
            start_sniff(argv[1], int(argv[2]))
        elif len(argv) > 1:
            start_sniff(argv[1])
        else:
            start_sniff()
    except ValueError:
        print("Invalid count value. It must be an integer.")
    except Exception as e:
        print(f"An error occurred: {e}")
