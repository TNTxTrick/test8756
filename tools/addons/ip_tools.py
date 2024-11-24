"""This module provides functions to analyze network matters."""

import ipaddress
import os
import re
import socket
import sys
from functools import cache
from time import sleep
from typing import List
from urllib.parse import urlparse

import requests
from colorama import Fore as F
from requests.exceptions import Timeout
from scapy.all import srp
from scapy.layers.l2 import ARP, Ether


def __is_cloud_flare(target: str) -> None:
    """Check if the target is protected by CloudFlare.

    Args:
        - target - The URL to be checked in the CloudFlare protection networks

    Returns:
        None
    """
    domain, _ = get_target_domain(target)
    try:
        origin = socket.gethostbyname(domain)
        iprange = requests.get("https://www.cloudflare.com/ips-v4", timeout=10).text
        ipv4 = [row.rstrip() for row in iprange.splitlines()]
        for ip in ipv4:
            if ipaddress.ip_address(origin) in ipaddress.ip_network(ip):
                print(
                    f"\n{F.RED}[!] {F.CYAN}This website is protected by CloudFlare, this attack may not produce the desired results.{F.RESET}"
                )
                sleep(1)
                return
    except (Timeout, socket.gaierror):
        print(
            f"{F.RED}\n[!] {F.CYAN}It was not possible to check for CloudFlare protection!{F.RESET}"
        )
        sleep(1)


def get_target_address(target: str) -> str:
    """Get target's URL formatted with HTTP protocol and CloudFlare checked.

    Args:
        - target - The target's URL

    Returns:
        - url - The formatted and checked URL
    """
    url = set_target_http(target)
    __is_cloud_flare(url)
    return url


def set_target_http(target: str) -> str:
    """Get target's URL formatted with HTTP protocol.

    Args:
        - target - The target's URL

    Returns:
        - target - The target's URL with HTTP protocol
    """
    if not target.startswith("http"):
        target = f"http://{target}"
    return target


def get_target_domain(target: str) -> str:
    """Get target's domain.

    Args:
        - target - The target's URL

    Returns:
        - domain - The target's domain
    """
    parsed_uri = urlparse(target)
    domain, port = parsed_uri.netloc.split(":") if ":" in parsed_uri.netloc else (parsed_uri.netloc, 80)
    return domain, int(port)


def get_host_ip() -> str:
    """Get host's IP.

    Args:
        None

    Returns:
        - IP - The host's IP
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    except Exception:
        print(
            f"{F.RED}│   └───{F.MAGENTA}[!] {F.BLUE}Local IP cannot be found!{F.RESET}"
        )
        sys.exit(1)
    finally:
        s.close()
    return IP


def show_local_host_ips() -> None:
    """Show all IPs connected on the local network.

    Args:
        None

    Returns:
        None
    """
    print(f"{F.RED}│   │")
    print(
        f"{F.RED}│   ├───{F.MAGENTA} [!] {F.LIGHTCYAN_EX}Scanning Local Network...{F.RESET}"
    )
    print(f"{F.RED}│   │")
    print(f"{F.RED}│   ├───{F.BLUE} Available Hosts:{F.RESET}")
    print(f"{F.RED}│   │")

    try:
        hosts = __get_local_host_ips()
        if hosts:
            for host in hosts[1:-1]:
                print(f"{F.RED}│   │    {F.GREEN} {host}{F.RESET}")
        else:
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.RED}No Hosts Available!{F.RESET}")
    except Exception as e:
        print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.RED}Error: {str(e)}{F.RESET}")


@cache
def __get_local_host_ips() -> List[str]:
    """Get all host IPs connected on the local network.

    Args:
        None

    Returns:
        - hosts - A list containing all host IPs
    """
    try:
        report = (
            os.popen(f"nmap -sP {'.'.join(get_host_ip().split('.')[:3]) + '.1-255'}")
            .read()
            .split("\n")
        )
        pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
        hosts = [pattern.search(line)[0] for line in report if pattern.search(line)]
        return hosts
    except Exception as e:
        print(f"{F.RED}│   └───{F.MAGENTA}[!] {F.RED}Error: {str(e)}{F.RESET}")
        return []


@cache
def __get_mac(target: str) -> str:
    """Get the MAC address of the target.

    Args:
        - target - The target that we want to get the MAC address

    Returns:
        - mac_addr - The MAC address itself
    """
    while True:
        try:
            arp_request = ARP(pdst=target)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            ans = srp(packet, timeout=5, verbose=False)[0]
            mac_addr = ans[0][1].hwsrc
            return mac_addr
        except IndexError:
            continue
        except Exception as e:
            print(f"{F.RED}│   └───{F.MAGENTA}[!] {F.RED}Error: {str(e)}{F.RESET}")
            return ""
