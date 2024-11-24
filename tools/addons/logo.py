"""This module provides a function that prints the logo's application."""

import os
from colorama import Fore as F

def show_logo() -> None:
    """Print the application logo.

    Args:
        None

    Returns:
        None
    """
    logo = r"""
// ______                                             ___
// | ___ \                                           /   |
// | |_/ / _   _  _ __   _ __   _   _          ____ / /| | _ __  __  __
// |  __/ | | | || '_ \ | '_ \ | | | |        |_  // /_| || '_ \ \ \/ /
// | |    | |_| || |_) || |_) || |_| |         / / \___  || | | | >  <
// \_|     \__,_|| .__/ | .__/  \__, |        /___|    |_/|_| |_|/_/\_\
//               | |    | |      __/ | ______
//               |_|    |_|     |___/ |______|

    """

    print(f"{F.RED}{logo}")
    print("├─── DDOS TOOL")
    print("├─── AVAILABLE METHODS")
    print("├─── LAYER 7: HTTP | HTTP-PROXY | SLOWLORIS | SLOWLORIS-PROXY")
    if os.name != "nt":
        print("├─── LAYER 4: SYN-FLOOD")
        print("├─── LAYER 2: ARP-SPOOF | DISCONNECT")
    print("├───┐")
