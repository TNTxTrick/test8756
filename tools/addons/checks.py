"""This module provides functions to check inputs."""

import os
import sys
from typing import Union

import requests
from colorama import Fore as F
from requests.exceptions import ConnectionError, InvalidURL, ReadTimeout

from tools.addons.ip_tools import __get_local_host_ips, set_target_http


def check_method_input() -> str:
    """Check if the method name is valid.

    Args:
        None

    Returns:
        - method - A valid method name
    """
    valid_methods = [
        "http",
        "http-proxy",
        "slowloris",
        "slowloris-proxy",
        "syn-flood",
        "arp-spoof",
        "disconnect",
    ]

    while True:
        method = input(f"{F.RED}│   ├─── METHOD: {F.RESET}").lower()
        if method in valid_methods and not (method in ["syn-flood", "arp-spoof", "disconnect"] and os.name == "nt"):
            if method in ["syn-flood", "arp-spoof", "disconnect"] and os.geteuid() != 0:
                print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}This attack needs Super User privileges!{F.RESET}")
                print(f"{F.RED}│   └───{F.MAGENTA} [!] {F.BLUE}Run: {F.GREEN}sudo {os.popen('which python').read().strip()} overload.py\n{F.RESET}")
                sys.exit(1)
            return method
        else:
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}Type a valid method!{F.RESET}")


def check_number_input(x: str) -> int:
    """Check if an input is an integer number greater than zero.

    Args:
        - x - The name of the input field

    Returns:
        - y - A valid value
    """
    while True:
        try:
            y = int(input(f"{F.RED}│   ├─── {x.upper()}: {F.RESET}"))
            if y > 0:
                return y
            else:
                raise ValueError
        except ValueError:
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}This value must be an integer number greater than zero!{F.RESET}")


def check_http_target_input() -> str:
    """Check if the target is reachable over HTTP.

    Args:
        None

    Returns:
        - target - A valid target URL
    """
    while True:
        target = input(f"{F.RED}│   ├─── URL: {F.RESET}")
        try:
            requests.get("https://google.com", timeout=4)
            requests.get(set_target_http(target), timeout=4)
            return target
        except (ConnectionError, ReadTimeout):
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}Device is not connected to the internet!{F.RESET}")
        except InvalidURL:
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}Invalid URL!{F.RESET}")


def check_local_target_input() -> str:
    """Check if the target is in the local network.

    Args:
        None

    Returns:
        - target - A valid local IP address
    """
    hosts = __get_local_host_ips()
    while True:
        target = input(f"{F.RED}│   ├─── IP: {F.RESET}")
        if target in hosts:
            return target
        else:
            print(f"{F.RED}│   ├───{F.MAGENTA} [!] {F.BLUE}Cannot connect to {F.CYAN}{target}{F.BLUE} on the local network!{F.RESET}")
