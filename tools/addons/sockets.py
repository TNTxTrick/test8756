"""This module provides functions to create socket instances."""

import json
import random
import socket
import sys
import warnings
from typing import Dict, List, Tuple, Union

import requests
import socks
from colorama import Fore as F
from requests.exceptions import ConnectionError, Timeout

from tools.addons.ip_tools import get_target_domain

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Load user agents from JSON file
with open("tools/L7/user_agents.json", "r", encoding="utf-8") as agents:
    user_agents = json.load(agents)["agents"]

def get_socks_proxies() -> List[Dict[str, str]]:
    """Return a list of available SOCKS proxies.

    Args:
        None

    Returns:
        - proxies: A list of dictionaries containing SOCKS proxies in the form of address:port
    """
    try:
        with requests.get(
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all&ssl=all&anonymity=all",
            verify=False,
            timeout=10,
        ) as proxy_list:
            proxies = []
            for proxy in proxy_list.text.split("\r\n"):
                if proxy:
                    addr, port = proxy.split(":")
                    proxies.append({"addr": addr, "port": port})
    except Timeout:
        print(f"\n{F.RED}[!] {F.CYAN}It was not possible to connect to the proxies!{F.RESET}")
        sys.exit(1)
    except ConnectionError:
        print(f"\n{F.RED}[!] {F.CYAN}Device is not connected to the Internet!{F.RESET}")
        sys.exit(1)

    return proxies

proxies = get_socks_proxies()

def create_socket_proxy(target: str) -> Tuple[socket.socket, Dict[str, str]]:
    """Create a socket through a SOCKS proxy.

    Args:
        - target: The target URL

    Returns:
        - sock: The socket associated with the communication
        - proxy: The proxy's address and port
    """
    global proxies
    while True:
        try:
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)

            while True:
                proxy = random.choice(proxies)
                proxy_addr, proxy_port = proxy["addr"], proxy["port"]
                try:
                    proxy_port = int(proxy_port)
                except ValueError:
                    continue
                else:
                    sock.set_proxy(socks.PROXY_TYPE_SOCKS5, proxy_addr, proxy_port)
                    break

            connect_socket(target, sock)
            break
        except (socket.timeout, socket.error):
            try:
                proxies.remove(proxy)
            except ValueError:
                proxies = get_socks_proxies()
            continue
    return sock, proxy

def create_socket(target: str) -> socket.socket:
    """Create a socket directly.

    Args:
        - target: The target URL

    Returns:
        - sock: The socket associated with the communication
    """
    while True:
        try:
            sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            connect_socket(target, sock)
            break
        except (socket.timeout, socket.error):
            continue
    return sock

def connect_socket(target: str, sock: socket.socket) -> None:
    """Connect the socket to the target.

    Args:
        - target: The target URL
        - sock: The socket used to connect to the target

    Returns:
        None
    """
    domain, port = get_target_domain(target)
    ip = socket.gethostbyname(domain)
    sock.connect((ip, port))

    sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
    sock.send(f"User-Agent: {random.choice(user_agents)}\r\n".encode("utf-8"))
    sock.send("Accept-Language: en-US,en;q=0.5\r\n".encode("utf-8"))
